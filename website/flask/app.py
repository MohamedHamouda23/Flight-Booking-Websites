# Name: Mohamed Hammouda | Student ID: 23077543

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import mysql.connector 
from flask_bcrypt import Bcrypt 
from datetime import datetime, timedelta
import random
import string
from fpdf import FPDF
from functools import wraps
from datetime import datetime 

app = Flask(__name__,
            template_folder='../template', 
            static_folder='../static')  
bcrypt = Bcrypt(app)
app.secret_key = 'Horizon_Uwe_project'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_log'):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'Admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function



def get_db_connection():
    return mysql.connector.connect(
        host='127.0.0.1',  
        user='root',
        password='hamouda22',
        database='Horizon_travel' 
    )

def execute_query(query, params=None, fetch_one=False, commit=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()



def generate_random_number(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"

def calculate_discount_rate(days_until_departure):
    if 80 <= days_until_departure <= 90:
        return 0.25
    elif 60 <= days_until_departure < 80:
        return 0.15
    elif 45 <= days_until_departure < 60:
        return 0.10
    return 0

def calculate_refund_amount(departure_date, booking_price):
    current_time = datetime.now()
    if departure_date.date() > (current_time + timedelta(days=60)).date():
        return booking_price
    elif (current_time + timedelta(days=31)).date() <= departure_date.date() <= (current_time + timedelta(days=60)).date():
        return booking_price * 0.40
    return booking_price * 0

def create_pdf_ticket(journey, user_details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PASSENGER AND TICKET INFORMATION", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.ln(4)
    pdf.cell(0, 10, f"Passenger Name: {user_details[1]} {user_details[2]}", ln=True)
    pdf.cell(0, 10, f"Booking Reference : {journey.get('booking_ID', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"E-Ticket Number: {journey.get('receipt_number', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Issued By: {journey.get('Travel_Company', 'N/A')}", ln=True)
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "TRAVEL INFORMATION", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(4)
    pdf.cell(0, 10, f"Flight Number : {journey.get('Journey_ID', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Departure: {journey.get('departure_city', 'N/A')} at {journey.get('departure_time', 'N/A')} on {journey.get('departure_date', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Arrival: {journey.get('destination_city', 'N/A')} at {journey.get('arrival_time', 'N/A')} on {journey.get('arrival_date', 'N/A')}", ln=True)
    pdf.cell(0, 10, "Class: Economy", ln=True)
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FARE AND ADDITIONAL INFORMATION", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(4)
    pdf.cell(0, 10, f"Payment ID: {journey.get('pay_id', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Passengers: {journey.get('booked_seats', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Total Fare: {journey.get('booking_price', 'N/A')} £", ln=True)
    pdf.cell(0, 10, "Form of Payment: CREDIT CARD", ln=True)
    return pdf



def handle_seat_updates(journey_id, class_type, booked_seats, operation):
    column = "business_seats" if class_type.lower() == "business" else "economy_seats"
    change = -booked_seats if operation == "reserve" else booked_seats
    execute_query(
        f"UPDATE seats SET {column} = {column} + %s WHERE Journey_ID = %s",
        (change, journey_id),
        commit=True
    )

def update_booking_journey(booking_id, new_journey_id):
    execute_query(
        "UPDATE Bookings SET Journey_ID = %s WHERE Booking_ID = %s",
        (new_journey_id, booking_id),
        commit=True
    )
    return True

def update_payment_amount(pay_id, amount_change):
    if amount_change > 0:
        execute_query(
            "UPDATE payments SET payment_amount = payment_amount + %s WHERE Pay_ID = %s",
            (amount_change, pay_id),
            commit=True
        )
    elif amount_change < 0:
        execute_query(
            "UPDATE payments SET payment_amount = payment_amount - %s WHERE Pay_ID = %s",
            (-amount_change, pay_id),
            commit=True
        )

def get_user_bookings(user_id):
    return execute_query("""
        SELECT 
            b.booking_ID,
            j.Journey_ID,
            jd.departure_city,
            jd.destination_city,
            jd.departure_date,
            jd.arrival_date,
            jd.departure_time,
            jd.arrival_time,
            bd.class_type,
            bd.booked_seats,
            p.Pay_ID,
            p.payment_amount,
            p.receipt_number,
            t.Co_name AS Travel_Company,
            bd.booking_status
        FROM Bookings b
        INNER JOIN Booking_details bd ON b.booking_ID = bd.booking_ID
        INNER JOIN Journey j ON b.Journey_ID = j.Journey_ID
        INNER JOIN journey_details jd ON j.Journey_ID = jd.Journey_ID
        INNER JOIN TravelCO t ON j.Tco_ID = t.Tco_ID
        INNER JOIN payments p ON b.Pay_ID = p.Pay_ID
        WHERE b.user_ID = %s AND bd.booking_status = 'Confirmed'
    """, (user_id,))



@app.route('/about')
def about():
    return render_template('About us.html')

@app.route('/confirm_cancel', methods=['GET', 'POST'])
@login_required
def confirm_cancel():
    if request.method == 'POST':
        journey = session.get('selected_booking')
        execute_query(
            "UPDATE Booking_details SET booking_status = 'Cancelled' WHERE booking_ID = %s",
            (journey.get('booking_ID'),),
            commit=True
        )
        execute_query(
            "UPDATE payments SET pay_status = 'Cancelled' WHERE pay_id = %s",
            (journey.get('pay_id'),),
            commit=True
        )
        handle_seat_updates(
            journey.get('Journey_ID'),
            journey.get('class_type'),
            journey.get('booked_seats'),
            "release"
        )
        return redirect(url_for('account'))
    return render_template('Booking_Control.html', 
                         selected_booking=session.get('selected_booking'),
                         confirm_cancel_url=url_for('confirm_cancel'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        user_log = execute_query(
            "SELECT * FROM users_details WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )
        if user_log:
            session['user_log'] = user_log
            bookings_data = get_user_bookings(user_id)
            all_user_bookings = [{
                "booking_ID": b[0],
                "Journey_ID": b[1],
                "departure_city": b[2],
                "destination_city": b[3],
                "departure_date": str(b[4]),
                "arrival_date": str(b[5]),
                "departure_time": str(b[6]),
                "arrival_time": str(b[7]),
                "class_type": b[8],
                "booked_seats": b[9],
                "pay_id": b[10],
                "receipt_number": b[12],
                "booking_price": b[11],
                "Travel_Company": b[13]
            } for b in bookings_data]
            session['all_user_bookings'] = all_user_bookings
            return render_template('Account.html', user=user_log, bookings=all_user_bookings)

    elif request.method == 'POST':
        fname_edit = request.form['first_name']
        lname_edit = request.form['last_name']
        phone_edit = request.form['phone']
        email_edit = request.form['email']
        old_password = request.form['password']
        new_password = request.form['new_password']
        stored_password = session.get('password')
        user_log = session.get('user_log')
        user_email = user_log[4] if user_log else None

        if execute_query("SELECT email FROM users_details WHERE email = %s AND user_id != %s", 
                        (email_edit, user_id)):
            return render_template('Account.html', 
                                user=user_log, 
                                bookings=session.get('all_user_bookings', []),
                                error_message="Email already exists")
        
        count_query = """
            SELECT COUNT(DISTINCT user_id) 
            FROM users_details 
            WHERE tel_number = %s AND user_id != %s
        """
        phone_count = execute_query(count_query, (phone_edit, user_id))

        if phone_count and phone_count[0][0] >= 2:  
            return render_template(
                'Account.html',
                user=user_log,
                bookings=session.get('all_user_bookings', []),
                error_message="This phone number is already linked to two accounts."
    )

        if not old_password.strip() and not new_password.strip():
            execute_query(
                "UPDATE users_details SET f_name=%s, l_name=%s, tel_number=%s, email=%s WHERE email=%s",
                (fname_edit, lname_edit, phone_edit, email_edit, user_email),
                commit=True
            )
        else:
            if bcrypt.check_password_hash(stored_password, old_password) and new_password.strip():
                hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                execute_query(
                    "UPDATE users_details SET f_name=%s, l_name=%s, tel_number=%s, email=%s, password=%s WHERE email=%s",
                    (fname_edit, lname_edit, phone_edit, email_edit, hashed_new_password, user_email),
                    commit=True
                )
                session['password'] = hashed_new_password
            elif not bcrypt.check_password_hash(stored_password, old_password):
                return render_template('Account.html', 
                                     user=user_log, 
                                     bookings=session.get('all_user_bookings', []),
                                     error_message="The password is incorrect")
            else:
                return render_template('Account.html', 
                                     user=user_log, 
                                     bookings=session.get('all_user_bookings', []),
                                     error_message="Leave the field blank to avoid changing the password")

        updated_user = execute_query(
            "SELECT * FROM users_details WHERE email = %s",
            (email_edit,),
            fetch_one=True
        )
        if updated_user:
            session['user_log'] = updated_user
            
    return render_template('Account.html', 
                             user=updated_user, 
                             bookings=session.get('all_user_bookings', []))

@app.route('/control', methods=['GET', 'POST'])
@login_required
def control():
    action = request.form.get('action')
    all_bookings = session.get('all_user_bookings', [])
    selected_booking_ID = request.form.get('booking_id')

    journey = next((b for b in all_bookings if str(b.get('booking_ID')) == str(selected_booking_ID)), 
                  session.get('selected_booking'))
    session['selected_booking'] = journey

    departure_date = datetime.strptime(journey.get('departure_date'), '%Y-%m-%d')
    refund = calculate_refund_amount(departure_date, journey.get('booking_price'))
    
    additional_payment=0
    if request.method == 'POST':  
        if action == "ticket":  
            user_details = session.get('user_log')
            pdf = create_pdf_ticket(journey, user_details)
            pdf_filename = "boarding pass.pdf"
            pdf.output(pdf_filename)
            return send_file(pdf_filename, as_attachment=True)
        
        elif action == "delete":
            return render_template('Booking_Control.html', 
                                selected_booking=journey,
                                refund=refund, datetime=datetime)

        elif action == "edit":
            date = request.form.get('date')
            if not date:
                return render_template('Booking_Control.html',
                                    selected_booking=journey,refund=refund, datetime=datetime)

            selected_booking = journey
            formatted_date = datetime.strptime(date, '%d/%m/%Y').date()
            current_time = datetime.now()

            all_user_updates = []
            seen_journeys = set()

            journeys = execute_query("""
                SELECT
                    Journey_Details.Journey_ID,
                    TravelCO.Co_name,
                    Journey_Details.departure_city,
                    Journey_Details.destination_city,
                    Journey_Details.departure_date,
                    Journey_Details.arrival_date,
                    Journey_Details.departure_time,
                    Journey_Details.arrival_time,
                    seats.economy_seats,
                    seats.business_seats,
                    Journey_Details.base_price
                FROM TravelCO
                INNER JOIN Journey ON TravelCO.Tco_ID = Journey.Tco_ID
                INNER JOIN Journey_Details ON Journey.Journey_ID = Journey_Details.Journey_ID
                INNER JOIN seats ON Journey.Journey_ID = seats.Journey_ID
                WHERE 
                    Journey_Details.departure_city = %s 
                    AND Journey_Details.destination_city = %s 
                    AND Journey_Details.departure_date = %s
            """, (
                selected_booking["departure_city"],
                selected_booking["destination_city"],
                formatted_date
            ))

            for journey in journeys:
                class_type = selected_booking["class_type"]
                booked_seats = selected_booking["booked_seats"]
                base_price = journey[10] * (2 if class_type.lower() == "business" else 1) * booked_seats
                
                days_until_departure = (journey[4] - current_time.date()).days
                discount_rate = calculate_discount_rate(days_until_departure)
                price_after_discount = base_price * (1 - discount_rate)
                
                old_price = float(selected_booking["booking_price"])
                price_difference = old_price - price_after_discount
                refund = round(price_difference, 2) if price_after_discount < old_price else 0
                additional_payment = round(-price_difference, 2) if price_after_discount > old_price else 0
                
                journey_key = (journey[0], journey[2], journey[3], journey[4], journey[6])
                
                if (journey[2] == selected_booking["departure_city"] and 
                    journey[3] == selected_booking["destination_city"] and 
                    journey[0] != selected_booking["Journey_ID"]):
                    
                    journey_departure_time = (datetime.min + journey[6]).time()
                    journey_departure_datetime = datetime.combine(journey[4], journey_departure_time)
                    time_difference = journey_departure_datetime - current_time

                    if (time_difference > timedelta(hours=3) and (journey[4] == formatted_date)):
                        if ((class_type.lower() == "business" and int(journey[9]) >= booked_seats) or 
                            (class_type.lower() == "economy" and int(journey[8]) >= booked_seats)):

                            if journey_key not in seen_journeys:
                                seen_journeys.add(journey_key)
                                all_user_updates.append({
                                    "booking_ID": selected_booking["booking_ID"],
                                    "Journey_ID": journey[0],
                                    "departure_city": journey[2],
                                    "destination_city": journey[3],
                                    "departure_date": str(journey[4]),
                                    "arrival_date": str(journey[5]),
                                    "departure_time": str(journey[6]),
                                    "arrival_time": str(journey[7]),
                                    "class_type": class_type,
                                    "booked_seats": booked_seats,
                                    "pay_id": selected_booking["pay_id"],
                                    "receipt_number": selected_booking["receipt_number"],
                                    "booking_price": round(price_after_discount, 2),
                                    "Travel_Company": journey[1],
                                    "economy_seats": journey[8],
                                    "business_seats": journey[9],
                                    "refund": refund,
                                    "additional_payment": additional_payment
                                })

            session['all_user_updates'] = all_user_updates
            session['additional_payment'] = additional_payment
            session['refund'] = refund

            if not all_user_updates:
                return render_template('Booking_Control.html',
                                    selected_booking=selected_booking, datetime=datetime,
                                    error_message="There are no available flights for the selected date")
            return render_template('availability.html', 
                                 all_user_updates=all_user_updates, 
                                 refund=refund, 
                                 additional_payment=additional_payment, datetime=datetime)
    
    return render_template('Booking_Control.html', 
                         selected_booking=journey,
                         refund=refund, datetime=datetime)



@app.route('/', methods=['GET', 'POST'])
def home():

    session.pop('additional_payment', None)
    session.pop('refund', None)
    now = datetime.now()

    availability_conditions = """
        WHERE 
            (jd.departure_date + INTERVAL jd.departure_time HOUR_SECOND) > ADDTIME(NOW(), '01:00:00')
            AND (jd.departure_date + INTERVAL jd.departure_time HOUR_SECOND) <= DATE_ADD(NOW(), INTERVAL 3 MONTH)
            AND (s.economy_seats > 0 OR s.business_seats > 0)
    """

    try:
        available_cities = [row[0] for row in execute_query(f"""
            SELECT DISTINCT jd.departure_city 
            FROM journey_details jd
            JOIN seats s ON jd.Journey_ID = s.Journey_ID
            {availability_conditions}
            ORDER BY jd.departure_city
        """)]

        route_pairs = execute_query(f"""
            SELECT DISTINCT jd.departure_city, jd.destination_city
            FROM journey_details jd
            JOIN seats s ON jd.Journey_ID = s.Journey_ID
            {availability_conditions}
            ORDER BY jd.departure_city, jd.destination_city
        """)

        available_dates = {
            f"{row[0]}-{row[1]}": row[2].split(',') if row[2] else []
            for row in execute_query(f"""
                SELECT jd.departure_city, jd.destination_city, 
                       GROUP_CONCAT(DISTINCT jd.departure_date ORDER BY jd.departure_date SEPARATOR ',') as dates
                FROM journey_details jd
                JOIN seats s ON jd.Journey_ID = s.Journey_ID
                {availability_conditions}
                GROUP BY jd.departure_city, jd.destination_city
            """)
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        available_cities, route_pairs, available_dates = [], [], {}

    if request.method == 'POST':
        departure = request.form['departure']
        destination = request.form['destination']
        flight_class = request.form['Type']
        departure_date = request.form['departure_date']
        booked_seats = int(request.form['booked_seats'])

        route_key = f"{departure}-{destination}"
        if route_key not in available_dates or departure_date not in available_dates[route_key]:
            return render_home_with_error(
                available_cities, route_pairs, available_dates,
                "No flights available for the selected route/date",
                departure, destination, flight_class, departure_date, booked_seats
            )

        try:
            selected_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            session.pop('matching_journeys', None)
            session.pop('Type', None)
            session.pop('booked_seats', None)

            base_query = """
                SELECT j.Journey_ID, t.Co_name, j.departure_city, j.destination_city,
                       j.departure_date, j.arrival_date, j.departure_time, j.arrival_time,
                       s.economy_seats, s.business_seats, j.base_price
                FROM TravelCO t
                INNER JOIN Journey jn ON t.Tco_ID = jn.Tco_ID
                INNER JOIN Journey_Details j ON jn.Journey_ID = j.Journey_ID
                INNER JOIN seats s ON jn.Journey_ID = s.Journey_ID
                WHERE j.departure_city = %s
                  AND j.destination_city = %s
                  AND j.departure_date = %s
                  AND (j.departure_date + INTERVAL j.departure_time HOUR_SECOND) > ADDTIME(%s, '01:00:00')
                  AND (j.departure_date + INTERVAL j.departure_time HOUR_SECOND) <= DATE_ADD(%s, INTERVAL 3 MONTH)
                  AND ((%s = 'Business' AND s.business_seats >= %s) OR (%s = 'Economy' AND s.economy_seats >= %s))
            """

            if selected_date == now.date():
                params = (departure, destination, selected_date, now, now, 
                         flight_class, booked_seats, flight_class, booked_seats)
            else:
                base_query = base_query.replace("ADDTIME(%s, '01:00:00')", "ADDTIME(NOW(), '01:00:00')")
                base_query = base_query.replace("DATE_ADD(%s, INTERVAL 3 MONTH)", "DATE_ADD(NOW(), INTERVAL 3 MONTH)")
                params = (departure, destination, selected_date, 
                         flight_class, booked_seats, flight_class, booked_seats)

            matching_journeys = execute_query(base_query, params)

            if not matching_journeys:
                seat_info = execute_query("""
                    SELECT s.economy_seats, s.business_seats
                    FROM Journey_Details jd
                    JOIN seats s ON jd.Journey_ID = s.Journey_ID
                    WHERE jd.departure_city = %s
                    AND jd.destination_city = %s
                    AND jd.departure_date = %s
                """, (departure, destination, selected_date))
                
                available_seats = seat_info[0] if seat_info else (0, 0)
                economy_available, business_available = available_seats
                suggested_msg = f"Only {business_available if flight_class == 'Business' else economy_available} {flight_class.lower()} class seats are available. Please adjust your booking."
                
                return render_home_with_error(
                    available_cities, route_pairs, available_dates,
                    suggested_msg, departure, destination, flight_class, 
                    departure_date, booked_seats
                )

            updated_journeys = process_matching_journeys(matching_journeys, flight_class, booked_seats, now)
            
            session['matching_journeys'] = updated_journeys
            session['Type'] = flight_class
            session['booked_seats'] = booked_seats

            return render_template('availability.html', matching_journeys=updated_journeys)

        except Exception as e:
            return render_home_with_error(
                available_cities, route_pairs, available_dates,
                str(e), departure, destination, flight_class, 
                departure_date, booked_seats
            )

    return render_template('Home.html',
                         available_cities=available_cities,
                         route_pairs=route_pairs,
                         available_dates=available_dates)


def render_home_with_error(available_cities, route_pairs, available_dates, 
                          error_message, departure, destination, 
                          flight_class, departure_date, booked_seats):
    return render_template('Home.html',
                         available_cities=available_cities,
                         route_pairs=route_pairs,
                         available_dates=available_dates,
                         error_message=error_message,
                         departure=departure,
                         destination=destination,
                         Type=flight_class,
                         departure_date=departure_date,
                         booked_seats=booked_seats)

def process_matching_journeys(journeys, flight_class, booked_seats, now):
    updated_journeys = []
    for journey in journeys:
        base_price = journey[10] * (2 if flight_class == "Business" else 1) * booked_seats
        days_until_departure = (journey[4] - now.date()).days
        discount_rate = calculate_discount_rate(days_until_departure)
        price_after_discount = base_price * (1 - discount_rate)

        updated_journeys.append((
            journey[0], journey[1], journey[2], journey[3],
            journey[4].strftime('%d/%m/%Y'), journey[5].strftime('%d/%m/%Y'),
            format_timedelta(journey[6]), format_timedelta(journey[7]),
            journey[8], journey[9], base_price, discount_rate * 100, price_after_discount
        ))
    return updated_journeys


@app.route('/confirm_update', methods=['GET', 'POST'])
@login_required
def confirm_update():
    if request.method == 'POST':
        journey_id = request.form.get('journey_id')
        all_user_updates = session.get('all_user_updates', [])
        selected_booking = session.get('selected_booking')
        selected_journey = next((j for j in all_user_updates if str(j['Journey_ID']) == str(journey_id)), None)

        if selected_journey:
            session['selected_journey'] = selected_journey
            old_price = float(selected_booking["booking_price"])
            new_price = float(selected_journey["booking_price"])
            price_difference = new_price - old_price

            if price_difference != 0:
                session['additional_payment'] = max(0, round(price_difference, 2))
                session['refund'] = max(0, round(-price_difference, 2))
                return render_template("payment details.html",
                                   additional_payment=session['additional_payment'],
                                   refund=session['refund'])
            else:
             
                
                if update_booking_journey(selected_booking['booking_ID'], selected_journey['Journey_ID']):
                    return redirect(url_for('account'))

    return render_template('availability.html', all_user_updates=session.get('all_user_updates', []))

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if not session.get('basket') and not (session.get('additional_payment') or session.get('refund')):
        return redirect(url_for('confirmation'))

    selected_journey = session.get('selected_journey')
    user_id = session.get('user_id')
    class_type = session.get('Type')
    booked_seats = session.get('booked_seats')

    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if session.get('additional_payment') or session.get('refund'):
                selected_booking = session.get('selected_booking', {})
                booking_id = selected_booking.get('booking_ID')
                old_journey_id = selected_booking.get('Journey_ID')
                pay_id = selected_booking.get('pay_id')
                booked_seats = selected_booking.get('booked_seats')
                class_type = selected_booking.get('class_type')
                price_difference = (session.get('additional_payment', 0) - 
                                  session.get('refund', 0))

                update_booking_journey(booking_id, selected_journey["Journey_ID"])
                update_payment_amount(pay_id, price_difference)
                handle_seat_updates(old_journey_id, class_type, booked_seats, "release")
                handle_seat_updates(selected_journey["Journey_ID"], class_type, booked_seats, "reserve")

            else:
                user_receipt = generate_random_number()
                while execute_query("SELECT receipt_number FROM payments WHERE receipt_number = %s", 
                                   (user_receipt,), fetch_one=True):
                    user_receipt = generate_random_number()
                
                session['user_receipt'] = user_receipt

                cursor.execute(
                    "INSERT INTO payments (payment_amount, receipt_number, pay_status) VALUES (%s, %s, %s)",
                    (selected_journey[12], user_receipt, "Confirmed")
                )
                pay_id = cursor.lastrowid
                if not pay_id:
                    raise ValueError("Failed to get payment ID")

                cursor.execute(
                    "INSERT INTO Bookings (Journey_ID, user_ID, Pay_ID) VALUES (%s, %s, %s)",
                    (selected_journey[0], user_id, pay_id)
                )
                booking_id = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO Booking_details (booking_ID, booked_seats, class_type, booking_status) VALUES (%s, %s, %s, %s)",
                    (booking_id, booked_seats, class_type, "Confirmed")
                )

                handle_seat_updates(selected_journey[0], class_type, booked_seats, "reserve")

                conn.commit()
                session['allow_confirmation'] = True
            return redirect(url_for('confirmation'))

        except Exception as e:
            if conn:
                conn.rollback()
            app.logger.error(f"Payment processing error: {str(e)}")
            return redirect(url_for('payment'))
        finally:
            if conn:
                conn.close()

    return render_template('payment details.html', 
                        selected_journey=selected_journey,
                        additional_payment=session.get('additional_payment'),
                        refund=session.get('refund'))

@app.route('/availability', methods=['GET', 'POST'])
def availability():
    if not session.get('matching_journeys'):
        return render_template('home.html')

    matching_journeys = session.get('matching_journeys')  

    if request.method == 'POST':
        journey_ID = request.form.get('journey_id')  
        selected_journey = next((j for j in matching_journeys if str(j[0]) == str(journey_ID)), None)
        
        if selected_journey:
            session['selected_journey'] = selected_journey
            session['basket'] = selected_journey
            return redirect(url_for('basket'))

    return render_template('availability.html', matching_journeys=matching_journeys)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
    selected_journey = session.get('basket')  
    if request.method == 'POST':
        if not session.get('user_logged_in'):
            flash("Log in required: <a href='{}'>Log in</a>".format(url_for('log_in')))
            return redirect(url_for('basket'))  
        return redirect(url_for('payment')) 

    return render_template('Basket.html', selected_journey=selected_journey)

@app.route('/conformation', methods=['GET', 'POST'])
@login_required
def confirmation():
    if not session.get('allow_confirmation'):
        return redirect(url_for('home'))  
    
    for key in ['allow_confirmation', 'additional_payment', 'refund', 
                'matching_journeys', 'Type', 'receipt', 'booked_seats', 
                'selected_journey', 'basket']:
        session.pop(key, None)
        
    return render_template('Booking_confirmation.html')

@app.route('/control_panel', methods=['GET', 'POST'])
@admin_required
def control_panel():
    return render_template('control panel.html')

@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if session.get('user_log'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        email_input = request.form['email']
        password_input = request.form['password']
        
        user_log = execute_query("""
            SELECT ud.user_ID, ud.f_name, ud.l_name, ud.tel_number, ud.email, ud.password, ur.role
            FROM users_details ud
            INNER JOIN users u ON ud.user_ID = u.user_ID
            INNER JOIN users_role ur ON u.role_ID = ur.role_ID
            WHERE ud.email = %s
        """, (email_input,), fetch_one=True)

        if user_log and bcrypt.check_password_hash(user_log[5], password_input):
            session.update({
                'user_log': user_log,
                'user_id': user_log[0],
                'account_type': user_log[6],
                'user_logged_in': True,
                'email': email_input,
                'password': user_log[5]
            })
            return redirect(url_for('home'))
                
    return render_template('log in.html')

@app.route('/log_out', methods=['GET', 'POST'])
@login_required
def log_out():
    if request.method == 'POST':
        session.clear()
    return redirect(url_for('home'))

@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if  session.get('user_log'):
            return redirect(url_for('home'))
        
    if request.method == 'POST':
        form_data = {
            'f_name': request.form['f_name'],
            'l_name': request.form['l_name'],
            'email': request.form['email'],
            'tel_number': request.form['tel_number'],
            'password': request.form['password'],
            'confirm_password': request.form['confirm_password']
        }
        
        if execute_query("SELECT email FROM users_details WHERE email = %s", (form_data['email'],), fetch_one=True):
            return render_template('sign_up.html', error_message="Email already exists", **form_data)
        
        if len(execute_query("SELECT tel_number FROM users_details WHERE tel_number = %s", (form_data['tel_number'],))) > 1:
            return render_template('sign_up.html', error_message="Phone number linked to two accounts", **form_data)
        
        if form_data['password'] != form_data['confirm_password']:
            return render_template('sign_up.html', error_message="Passwords do not match", **{k: v for k, v in form_data.items() if k != 'password'})
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT role_ID FROM users_role WHERE role = %s", ('customer',))
            role_id = cursor.fetchone()
            
            if not role_id:
                cursor.execute("INSERT INTO users_role (role) VALUES (%s)", ('customer',))
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID()")
                role_id = cursor.fetchone()
            
            cursor.execute("INSERT INTO users (role_ID) VALUES (%s)", (role_id[0],))
            conn.commit()
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = cursor.fetchone()[0]
            
            hashed_password = bcrypt.generate_password_hash(form_data['password']).decode('utf-8')
            cursor.execute(
                "INSERT INTO users_details (user_ID, f_name, l_name, email, tel_number, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, form_data['f_name'], form_data['l_name'], form_data['email'], form_data['tel_number'], hashed_password)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return render_template('log in.html')
            
        except Exception as e:
            if 'conn' in locals() and conn:
                conn.rollback()
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()
            return f"An error occurred: {e}"
    
    return render_template('sign_up.html')



@app.route('/user_details', methods=['GET', 'POST'])
@admin_required

def users():
   
    return render_template('user details.html')

@app.route('/bookings_status', methods=['GET', 'POST'])
@admin_required

def bookings():
   
    
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                B.booking_ID, 
                Ud.user_ID, 
                Jd.Journey_ID, 
                Jd.departure_city, 
                Jd.destination_city, 
                Jd.departure_date, 
                Bd.booking_status
            FROM `Bookings` B
            INNER JOIN `Booking_details` Bd ON B.booking_ID = Bd.booking_ID  
            INNER JOIN `Journey` J ON B.Journey_ID = J.Journey_ID  
            INNER JOIN `journey_details` Jd ON J.Journey_ID = Jd.Journey_ID  
            INNER JOIN `users_details` Ud ON B.user_ID = Ud.user_ID
            WHERE B.booking_ID = %s
            """, (booking_id,))  

            matching_booking = cursor.fetchone()  
            if matching_booking:
                 session['booking'] = {
                    'booking_ID': matching_booking[0],
                    'user_ID': matching_booking[1],
                    'journey_ID': matching_booking[2],
                    'departure_city': matching_booking[3],
                    'destination_city': matching_booking[4],
                    'departure_date': matching_booking[5],
                    'booking_status': matching_booking[6]
                }
            else:
                return render_template('bookings status.html', error="Booking not found")
        except Exception as e:
            return render_template('bookings status.html', error=f"An error occurred: {e}")

    return render_template('bookings status.html',booking=session.get('booking'), )


@app.route('/journeys', methods=['GET', 'POST'])
@admin_required
def journeys():
   
    return render_template('journeys.html')

@app.route('/Reports', methods=['GET', 'POST'])
@admin_required
def Reports():
   
    
    report_data = None
    userName = session.get('user_log')  
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        journey_id = request.form.get('Journey_ID')

        if report_type == 'Journey sales':
            if journey_id:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute("SELECT Journey_ID FROM Journey WHERE Journey_ID = %s", (journey_id,))
                    if not cursor.fetchone():
                        return render_template('Reports.html', error="Journey not found")
                    else:
                        cursor.execute("""
                        SELECT 
                            J.Journey_ID, 
                            p.payment_amount, 
                            bd.booked_seats
                        FROM Journey J
                        INNER JOIN Bookings B ON J.Journey_ID = B.Journey_ID 
                        INNER JOIN Booking_details bd ON B.booking_ID = bd.booking_ID 
                        INNER JOIN payments p ON B.Pay_ID = p.Pay_ID
                        INNER JOIN journey_details jd ON J.Journey_ID = jd.Journey_ID
                        INNER JOIN users_details ud ON B.user_ID = ud.user_ID
                        WHERE J.Journey_ID = %s
                        AND bd.booking_status = 'confirmed'
                    """, (journey_id,))

                        report_data = cursor.fetchall()
                        total_Revenue = sum(payment[1] for payment in report_data)
                        total_bookedSeats = sum(seats[2] for seats in report_data)
                        num_bookings = len(report_data)
                        average_bookings = total_Revenue / num_bookings if num_bookings > 0 else 0
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        sales= {
                    'Title': "Sales for each journey",
                    'Journey_ID': journey_id,
                    'Total Revenue': total_Revenue,
                    'Average Bookings': average_bookings,
                    'Bookings Numbers': num_bookings,
                    'Ticket Numbers': total_bookedSeats,
                    'Report Generated At': current_time,
                    'By': [userName[1], userName[2]]
                }
                except Exception as e:
                    report_data = None
                finally:
                    conn.close()

            return render_template('Reports.html', sales=sales)

        elif report_type == "top customers":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users")
                users = cursor.fetchall()

                if not users:
                    return render_template('Reports.html', error="No users found")
                
                session.pop('sales', None)


                cursor.execute("""
                   SELECT 
                        u.user_ID, 
                        CONCAT(ud_details.f_name, ' ', ud_details.l_name) AS full_name, 
                        COALESCE(AVG(CASE WHEN bd.booking_status = 'Confirmed' THEN p.payment_amount ELSE NULL END), 0) AS average_expenses,
                        COUNT(CASE WHEN bd.booking_status IN ('Confirmed', 'Cancelled') THEN 1 END) AS total_bookings,
                        COUNT(CASE WHEN bd.booking_status = 'Cancelled' THEN 1 END) AS cancelled_journeys,
                        SUM(CASE WHEN bd.booking_status = 'Confirmed' THEN p.payment_amount ELSE 0 END) AS total_expenses
                    FROM 
                        Journey J
                    INNER JOIN 
                        Bookings B ON J.Journey_ID = B.Journey_ID 
                    INNER JOIN 
                        Booking_details bd ON B.booking_ID = bd.booking_ID 
                    INNER JOIN 
                        payments p ON B.Pay_ID = p.Pay_ID 
                    INNER JOIN 
                        journey_details jd ON J.Journey_ID = jd.Journey_ID  
                    INNER JOIN 
                        users_details ud_details ON B.user_ID = ud_details.user_ID  
                    INNER JOIN 
                        users u ON B.user_ID = u.user_ID
                    GROUP BY 
                        u.user_ID, ud_details.f_name, ud_details.l_name
                    ORDER BY 
                        total_expenses DESC, 
                        average_expenses DESC
                    LIMIT 10;
                """)
                report_data = cursor.fetchall()
                if not report_data:
                    return render_template('Reports.html', error="No top customers found")

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                full_name = [userName[1], userName[2]]

                session['top'] = {
                    'Title': "Top customers",
                    'Report Generated At': current_time,
                    'By': full_name,
                    'data': []
                }

                for row in report_data:
                    session['top']['data'].append({
                        'user_ID': row[0], 
                        'full_name': row[1], 
                        'average_expenses': row[2],
                        'total_bookings': row[3],
                        'cancelled_journeys': row[4],
                        'total_expenses': row[5]
                    })

                return render_template('Reports.html', top=session.get('top'))
            


            finally:
                conn.close()
    return render_template('Reports.html')



@app.route('/users', methods=['GET', 'POST'])
@admin_required

def users_control():
   
    option_type = request.form.get('option_type')
    print(session.get('user_log')[0])
    

    if request.method == 'POST':
        userID = request.form.get('userID')
 
        if str(userID) == str(session.get('user_log')[0]):
            return render_template('user details.html',error_message="you can't chnage your account from here", userForAdmin=session.get('userForAdmin'),option_type=option_type)

            

        if option_type == 'Modify User Details':

            if userID :
    

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_ID FROM users_details WHERE user_ID = %s", (userID,))
                    if not cursor.fetchone():
                        session.pop('userForAdmin',None)
                        return render_template('user details.html', notFound="user not found")
                    else:
                        cursor.execute("""
                        SELECT  
                        u.user_ID,  
                        ud.f_name,  
                        ud.l_name,  
                        ud.tel_number,  
                        ud.email,  
                        '***' AS password, 
                        ur.role AS user_role
                    FROM users_details ud  
                    INNER JOIN users u ON ud.user_ID = u.user_ID  
                    INNER JOIN users_role ur ON u.role_ID = ur.role_ID
                        WHERE u.user_ID = %s
                   
                    """, (userID,))

                        user_modification = cursor.fetchone()
                        session['userForAdmin'] = {
                            'user_ID':  user_modification[0],
                            'First name': user_modification[1],
                            'Last name': user_modification[2],
                            'phone number': user_modification[3],
                            'Email': user_modification[4],
                            'Password': user_modification[5],
                            'Role': user_modification[6]
                        }
                except Exception as e:
                    user_modification = None
            
                finally:
                    conn.close()
            
             
        elif option_type=='Add users':
            session.pop('userForAdmin',None)

            return render_template('user details.html',option_type=option_type)


        return render_template('user details.html', userForAdmin=session.get('userForAdmin'),option_type=option_type)
      
      
@app.route('/update_user', methods=['GET', 'POST'])
@admin_required
def update_user():
    
    if request.method == 'POST':
        if 'userForAdmin' not in session:
            return "No user data in session", 400

        updated_fields = {key[7:-1]: value if value.strip() else None for key, value in request.form.items() if key.startswith('fields[')}

        email = updated_fields.get("Email")
        phone_number = updated_fields.get("phone number")
        password = updated_fields.get("Password")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') if password else None

        try:
            conn = get_db_connection()
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT email FROM users_details WHERE email = %s", (email,))
            result = cursor.fetchone()
            existing_email = result[0] if result else None
            cursor.execute("SELECT COUNT(*) FROM users_details WHERE tel_number = %s AND user_ID != %s", 
                           (phone_number, updated_fields.get("user_ID")))
            count = cursor.fetchone()[0]
            
            
            if count > 1:
                return render_template('user details.html', userForAdmin=session.get('userForAdmin'),
                                       error_message="Phone number linked to two accounts.")
          

            elif existing_email and existing_email != session['userForAdmin']['Email'] :
               return render_template('user details.html', userForAdmin=session.get('userForAdmin'),
                           error_message="Email already exists")


            else:
                cursor.execute("""
                    UPDATE users_details 
                    SET 
                        f_name = COALESCE(%s, f_name), 
                        l_name = COALESCE(%s, l_name), 
                        tel_number = COALESCE(%s, tel_number), 
                        email = COALESCE(%s, email), 
                        password = COALESCE(%s, password)
                    WHERE user_ID = %s
                """, (
                    updated_fields.get("First name"), 
                    updated_fields.get("Last name"), 
                    phone_number, 
                    email, 
                    hashed_password,  
                    updated_fields.get("user_ID")
                ))

                cursor.execute("SELECT role_ID FROM users_role WHERE role = %s", (updated_fields.get("role"),))
                role_result = cursor.fetchone()
                role_id = role_result[0] if role_result else None  
                if role_id is not None:
                    cursor.execute("""
                        UPDATE users 
                        SET role_ID = %s
                        WHERE user_ID = %s
                    """, (role_id, updated_fields.get("user_ID")))
                
                conn.commit()

                session.pop('userForAdmin', None)
                return redirect(url_for('update_user'))

        
        finally:
            cursor.close()
            conn.close()

    return render_template('user details.html', userForAdmin=session.get('userForAdmin'))

@app.route('/delete_user', methods=['GET', 'POST'])
@admin_required
def delete_user():
    if request.method == 'POST':
        user_id = request.form.get('user_ID')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Pay_ID FROM Bookings WHERE user_ID = %s", (user_id,))
            payments = cursor.fetchall()
            for payment in payments:
                pay_id = payment[0]
                cursor.execute("UPDATE payments SET pay_status = 'unactive' WHERE Pay_ID = %s", (pay_id,))
            
            cursor.execute("""
                SELECT b.Journey_ID, bd.booked_seats, bd.class_type 
                FROM Bookings b
                JOIN Booking_details bd ON b.booking_ID = bd.booking_ID
                WHERE b.user_ID = %s AND bd.booking_status = 'Confirmed'
            """, (user_id,))
            bookings = cursor.fetchall()
            
            for booking in bookings:
                journey_id, booked_seats, class_type = booking
                if class_type == 'business':
                    cursor.execute("""
                        UPDATE seats 
                        SET business_seats = business_seats + %s 
                        WHERE Journey_ID = %s
                    """, (booked_seats, journey_id))
                else: 
                    cursor.execute("""
                        UPDATE seats 
                        SET economy_seats = economy_seats + %s 
                        WHERE Journey_ID = %s
                    """, (booked_seats, journey_id))
            
            cursor.execute("DELETE FROM users WHERE user_ID = %s", (user_id,))
            conn.commit()
            
            if 'userForAdmin' in session:
                session.pop('userForAdmin')
            

            
        except Exception as e:
            flash(f'Error deleting user: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('user details.html')

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required

def add_user():
   
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        role = request.form.get('role')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') if password else None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users_details WHERE email = %s", (email,))
            existing_email = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM users_details WHERE tel_number = %s", (phone_number,))
            count = cursor.fetchone()[0]

            if existing_email:
                return render_template('user details.html', userForAdmin=session.get('userForAdmin'),
                                       error_message="Email already exists",option_type="Add users")

            if count > 1:
                return render_template('user details.html', userForAdmin=session.get('userForAdmin'),
                                       error_message="Phone number linked to two accounts.",option_type="Add users")
                
            cursor.execute("SELECT role_ID FROM users_role WHERE role = %s", (role,))
            role_id = cursor.fetchone()
            cursor.execute("""
                    INSERT INTO users ( role_ID) 
                    VALUES (%s)
                """, (role_id))
            
            user_id = cursor.lastrowid 
            cursor.execute("""
                INSERT INTO users_details (user_ID,f_name, l_name, email, tel_number, password) 
                VALUES (%s,%s, %s, %s, %s, %s)
            """, (user_id,first_name, last_name, email, phone_number, hashed_password))

            conn.commit()
            return render_template('user details.html',option_type="Add users")

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

        finally:
            cursor.close()
            conn.close()

    return render_template('user details.html',option_type="Add users")
@app.route('/search_journey', methods=['GET', 'POST'])
@admin_required

def search_journey():
  
    
    if request.method == 'POST':
        JourneyID = request.form.get('JourneyID')

        if JourneyID:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT Journey_ID FROM Journey_Details WHERE Journey_ID = %s", (JourneyID,))
                if not cursor.fetchone():
                    session.pop('update_journey', None)
                    return render_template('journeys.html', 
                                          notFound="Journey not found",
                                          option_type="Modify journey")
                cursor.execute("""
                    SELECT
                        Journey_Details.Journey_ID,
                        TravelCO.Co_name,
                        Journey_Details.departure_city,
                        Journey_Details.destination_city,
                        Journey_Details.departure_date,
                        Journey_Details.arrival_date,
                        Journey_Details.departure_time,
                        Journey_Details.arrival_time,
                        Journey_Details.base_price
                    FROM TravelCO
                    INNER JOIN Journey
                        ON TravelCO.Tco_ID = Journey.Tco_ID
                    INNER JOIN Journey_Details
                        ON Journey.Journey_ID = Journey_Details.Journey_ID
                    WHERE Journey_Details.Journey_ID = %s
                """, (JourneyID,))

                journey_modification = cursor.fetchone()

                session['update_journey'] = {
                    'Departure City': journey_modification[2],
                    'Destination City': journey_modification[3],
                    'Departure Date': str(journey_modification[4]),
                    'Arrival Date': str(journey_modification[5]),
                    'Departure Time': str(journey_modification[6]),
                    'Arrival Time': str(journey_modification[7]),
                    'Base Price': journey_modification[8]
                }

                session['read_journey'] = {
                    'Journey_ID': journey_modification[0],
                    'Travel Company': journey_modification[1],
                }

            
            finally:
                conn.close()

    return render_template('journeys.html', 
                         update_journey=session.get('update_journey'),
                         option_type="Modify journey",
                         read_journey=session.get('read_journey'))


def validate_journey_data(departure, arrival, departure_datetime_str, arrival_datetime_str):

    if departure == arrival:
        return (False, "Departure can't be the same as destination.", None, None)
    
    departure_dt = datetime.strptime(departure_datetime_str, '%Y-%m-%dT%H:%M')
    arrival_dt = datetime.strptime(arrival_datetime_str, '%Y-%m-%dT%H:%M')

    
    if departure_dt >= arrival_dt:
        return (False, "Departure time must be before arrival time.", None, None)
    
    if departure_dt < datetime.now():
        return (False, "Departure time cannot be in the past.", None, None)
    
    if (arrival_dt - departure_dt) > timedelta(hours=10):
        return (False, "The time difference between departure and arrival cannot exceed 10 hours.", None, None)
    
    return (True, "", departure_dt, arrival_dt)

@app.route('/update_journey', methods=['POST'])
@admin_required
def update_journey():
    JourneyID = request.form.get('JourneyID')
    Departure = request.form.get('departure')  
    Arrival = request.form.get('arrival')      
    new_departure_time = request.form.get('new_departure_time')
    new_arrival_time = request.form.get('new_arrival_time')
    new_price = request.form.get('new_price')
    
    is_valid, error_message, departure_dt, arrival_dt = validate_journey_data(
        Departure, Arrival, new_departure_time, new_arrival_time
    )
    
    if not is_valid:
        return render_template('journeys.html', 
                            update_journey=session.get('update_journey'),
                            option_type="Modify journey",
                            read_journey=session.get('read_journey'),
                            error_message=error_message)

    Departure_Date = departure_dt.date()
    Departure_Time = departure_dt.time()
    Arrival_Date = arrival_dt.date()
    Arrival_Time = arrival_dt.time()  
        
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
            UPDATE Journey_Details
            SET 
                departure_city = %s, 
                destination_city = %s, 
                departure_date = %s, 
                arrival_date = %s, 
                departure_time = %s, 
                arrival_time = %s,
                base_price = %s
            WHERE Journey_ID = %s
        """, (
            Departure, 
            Arrival, 
            Departure_Date, 
            Arrival_Date, 
            Departure_Time, 
            Arrival_Time, 
            new_price,
            JourneyID
        ))

    conn.commit()        
    session['update_journey'] = {
            'Departure City': Departure,
            'Destination City': Arrival,
            'Departure Date': str(Departure_Date),
            'Arrival Date': str(Arrival_Date),
            'Departure Time': str(Departure_Time),
            'Arrival Time': str(Arrival_Time),
            'Base Price': new_price
        }
        
    session['journey_update_success'] = True
    
    return render_template('journeys.html', 
                            update_journey=session.get('update_journey'),
                            option_type="Modify journey",
                            read_journey=session.get('read_journey'))

@app.route('/add_journey', methods=['GET', 'POST'])
@admin_required
def add_journey():
    if request.method == 'POST':
        company = request.form.get('company')
        departure = request.form.get('departure')
        arrival = request.form.get('arrival')
        departure_datetime = request.form.get('departure_datetime') 
        arrival_datetime = request.form.get('arrival_datetime')     
        price = request.form.get('new_price')
        
        is_valid, error_message, departure_dt, arrival_dt = validate_journey_data(
            departure, arrival, departure_datetime, arrival_datetime
        )
        
        if not is_valid:
            return render_template('journeys.html', error_message=error_message)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Tco_ID FROM TravelCO WHERE Co_name = %s", (company,))
            tco_id = cursor.fetchone()[0]  
   
            cursor.execute("INSERT INTO journey (Tco_ID) VALUES (%s)", (tco_id,))
            journey_id = cursor.lastrowid 
            
            cursor.execute("""
                INSERT INTO journey_details (
                    Journey_ID, 
                    departure_city, 
                    destination_city, 
                    departure_date, 
                    arrival_date, 
                    departure_time, 
                    arrival_time, 
                    base_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            """, (
                journey_id, 
                departure, 
                arrival, 
                departure_dt.date(), 
                arrival_dt.date(), 
                departure_dt.time(), 
                arrival_dt.time(), 
                price
            ))
            
            cursor.execute("INSERT INTO seats (Journey_ID) VALUES (%s)", (journey_id,))
            
            conn.commit()
            return redirect(url_for('search_journey'))  

        finally:
            if conn:
                conn.close()

    return render_template('journeys.html')


@app.route('/delete_journey', methods=['GET', 'POST'])
@admin_required
def delete_journey():
    if request.method == 'POST':
        journey_id = request.form.get('Journey_ID')
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT Pay_ID FROM Bookings WHERE Journey_ID = %s", (journey_id,))
            payments = cursor.fetchall()
            for payment in payments:
                pay_id = payment[0]
                cursor.execute("UPDATE payments SET pay_status = 'unactive' WHERE Pay_ID = %s", (pay_id,))

            cursor.execute("DELETE FROM journey_details WHERE Journey_ID = %s", (journey_id,))
            cursor.execute("DELETE FROM seats WHERE Journey_ID = %s", (journey_id,))
            cursor.execute("DELETE FROM Bookings WHERE Journey_ID = %s", (journey_id,))
            cursor.execute("DELETE FROM journey WHERE Journey_ID = %s", (journey_id,))

            conn.commit()

        finally:
            cursor.close()
            conn.close()

    return render_template('journeys.html')



if __name__ == '__main__':

    app.run(debug=True)
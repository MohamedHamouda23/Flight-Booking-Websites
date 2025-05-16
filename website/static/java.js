// Name: Mohamed Hammouda | Student ID: 23077543

function closeErrorBox() {
  document.getElementById("box error-box").style.display = "none";
}

function toggleEditMode() {
  const viewMode = document.getElementById("view-mode");
  const editMode = document.getElementById("edit-mode");

  if (viewMode.style.display === "block") {
    viewMode.style.display = "none";
    editMode.style.display = "block";
  } else {
    viewMode.style.display = "block";
    editMode.style.display = "none";
  }
}

window.history.forward();
function noBack() {
  window.history.forward();
}

window.onload = noBack;
window.onpageshow = function (evt) {
  if (evt.persisted) noBack();
};
window.onunload = function () {};



function myFunction(event) {
  event.preventDefault(); 
  
  var refund = document.getElementById("refundValue").innerText;

  var confirmation = confirm(
    "By proceeding, your refund of " +
      refund +
      " £ will be issued directly to your account. Please confirm to proceed, or cancel to abort."
  );

  if (confirmation) {
    document.getElementById("refundInput").value = refund;
    document.getElementById("deleteForm").submit();
  } else {
    alert("Refund process has been canceled.");
  }
}

window.onload = function () {
  const isLoggedIn =
    localStorage.getItem("user_log") ||
    document.cookie.includes("user_log=true") ||
    false;

  if (isLoggedIn) {
    window.location.href = "/account";
  }
};

function isValidDateRange(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const maxDate = new Date(today);
  maxDate.setMonth(today.getMonth() + 3);

  date.setHours(0, 0, 0, 0);

  if (date < today) {
    return "The date cannot be in the past.";
  } else if (date > maxDate) {
    return "The date cannot be more than 3 months from today.";
  }
  return ""; 
}

function showError(message) {
  const existingError = document.getElementById("error-box");
  if (existingError) existingError.remove();

  const errorBox = document.createElement("div");
  errorBox.id = "error-box";
  errorBox.innerHTML = `
        <button onclick="closeErrorBox()">X</button>
        <p>${message}</p>
    `;
  document.body.prepend(errorBox);
}

function closeErrorBox() {
  const box = document.getElementById("error-box");
  if (box) box.remove();
}

function edit() {
  let newDate;
  const datePattern = /^\d{2}\/\d{2}\/\d{4}$/;

  while (true) {
    newDate = prompt("Enter the new date for your journey (DD/MM/YYYY):");
    if (newDate === null) return;

    if (!datePattern.test(newDate)) {
      alert("Invalid date format. Please use DD/MM/YYYY.");
      continue;
    }

    const [day, month, year] = newDate.split("/").map(Number);
    const enteredDate = new Date(year, month - 1, day);
    const validationMsg = isValidDateRange(enteredDate);

    if (validationMsg) {
      alert(validationMsg);
      continue;
    }

    break;
  }

  document.getElementById("dateInput").value = newDate;
  document.getElementById("dateForm").submit();
}



function isValidDateRange(selectedDate) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const maxDate = new Date(today);
  maxDate.setMonth(maxDate.getMonth() + 3);

  if (selectedDate < today) {
    return "Date cannot be in the past.";
  }

  if (selectedDate > maxDate) {
    return "Date cannot be more than 3 months in advance.";
  }

  return null;
}

function isValidDateTimeRange(departureDateTime, arrivalDateTime) {
  const dateError = isValidDateRange(departureDateTime);
  if (dateError) return dateError;

  if (arrivalDateTime <= departureDateTime) {
    return "Arrival date/time must be after departure date/time.";
  }

  return null;
}





function isValidDateRange(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const maxDate = new Date(today);
  maxDate.setMonth(today.getMonth() + 3);

  date.setHours(0, 0, 0, 0);

  if (date < today) {
    return "The date cannot be in the past.";
  } else if (date > maxDate) {
    return "The date cannot be more than 3 months from today.";
  }
  return "";
}

function initDateValidation() {
  const departureDateInput = document.getElementById('departure_date');

  if (departureDateInput) {
    departureDateInput.addEventListener('change', function() {
      const selectedDate = new Date(this.value);
      const errorMessage = isValidDateRange(selectedDate);

      if (errorMessage) {
        showError(errorMessage);
        this.value = "";
      }
    });
  }
}

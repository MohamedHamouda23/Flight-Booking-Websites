-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (arm64)
--
-- Host: 127.0.0.1    Database: Horizon_travel
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Booking_details`
--

DROP TABLE IF EXISTS `Booking_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Booking_details` (
  `booking_ID` int NOT NULL,
  `booked_seats` int NOT NULL,
  `class_type` enum('business','economy') NOT NULL,
  `booking_status` enum('Confirmed','Cancelled') NOT NULL,
  KEY `booking_ID` (`booking_ID`),
  CONSTRAINT `booking_details_ibfk_1` FOREIGN KEY (`booking_ID`) REFERENCES `Bookings` (`booking_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Booking_details`
--

/*!40000 ALTER TABLE `Booking_details` DISABLE KEYS */;
INSERT INTO `Booking_details` VALUES (1,1,'business','Confirmed'),(2,1,'economy','Confirmed'),(3,1,'economy','Confirmed'),(4,1,'business','Confirmed'),(5,1,'business','Confirmed'),(6,1,'economy','Confirmed'),(7,1,'business','Confirmed'),(8,5,'business','Confirmed');
/*!40000 ALTER TABLE `Booking_details` ENABLE KEYS */;

--
-- Table structure for table `Bookings`
--

DROP TABLE IF EXISTS `Bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bookings` (
  `booking_ID` int NOT NULL AUTO_INCREMENT,
  `Journey_ID` int NOT NULL,
  `user_ID` int NOT NULL,
  `Pay_ID` int NOT NULL,
  PRIMARY KEY (`booking_ID`),
  KEY `user_ID` (`user_ID`),
  KEY `Journey_ID` (`Journey_ID`),
  KEY `bookings_ibfk_5_idx` (`Pay_ID`),
  CONSTRAINT `booking1` FOREIGN KEY (`Pay_ID`) REFERENCES `payments` (`Pay_ID`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `booking2` FOREIGN KEY (`user_ID`) REFERENCES `users` (`user_ID`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `booking3` FOREIGN KEY (`Journey_ID`) REFERENCES `journey` (`Journey_ID`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bookings`
--

/*!40000 ALTER TABLE `Bookings` DISABLE KEYS */;
INSERT INTO `Bookings` VALUES (1,19,1,1),(2,45,1,2),(3,1,1,3),(4,34,2,4),(5,18,2,5),(6,41,2,6),(7,38,5,7),(8,42,6,8);
/*!40000 ALTER TABLE `Bookings` ENABLE KEYS */;

--
-- Table structure for table `journey`
--

DROP TABLE IF EXISTS `journey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journey` (
  `Journey_ID` int NOT NULL AUTO_INCREMENT,
  `Tco_ID` int DEFAULT NULL,
  PRIMARY KEY (`Journey_ID`),
  KEY `journey_idx` (`Tco_ID`),
  CONSTRAINT `journey` FOREIGN KEY (`Tco_ID`) REFERENCES `TravelCO` (`Tco_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journey`
--

/*!40000 ALTER TABLE `journey` DISABLE KEYS */;
INSERT INTO `journey` VALUES (1,1),(11,1),(22,1),(33,1),(42,1),(5,2),(14,2),(21,2),(34,2),(41,2),(3,3),(12,3),(26,3),(31,3),(46,3),(7,4),(17,4),(23,4),(38,4),(43,4),(2,5),(15,5),(29,5),(39,5),(8,6),(19,6),(25,6),(32,6),(45,6),(4,7),(13,7),(24,7),(35,7),(44,7),(10,8),(18,8),(30,8),(40,8),(9,9),(20,9),(28,9),(37,9),(6,10),(16,10),(27,10),(36,10);
/*!40000 ALTER TABLE `journey` ENABLE KEYS */;

--
-- Table structure for table `journey_details`
--

DROP TABLE IF EXISTS `journey_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journey_details` (
  `Journey_ID` int NOT NULL,
  `departure_city` varchar(100) NOT NULL,
  `destination_city` varchar(100) NOT NULL,
  `departure_date` date NOT NULL,
  `arrival_date` date NOT NULL,
  `departure_time` time NOT NULL,
  `arrival_time` time NOT NULL,
  `base_price` int NOT NULL,
  KEY `journey_details_idx` (`Journey_ID`),
  CONSTRAINT `journey_details` FOREIGN KEY (`Journey_ID`) REFERENCES `journey` (`Journey_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journey_details`
--

/*!40000 ALTER TABLE `journey_details` DISABLE KEYS */;
INSERT INTO `journey_details` VALUES (1,'Newcastle','Bristol','2024-10-15','2024-10-15','17:45:00','19:00:00',90),(2,'Bristol','Newcastle','2024-11-22','2024-11-22','09:00:00','10:15:00',90),(3,'Cardiff','Edinburgh','2024-12-05','2024-12-05','07:00:00','08:30:00',90),(4,'Bristol','Manchester','2025-01-10','2025-01-10','12:30:00','13:30:00',80),(5,'Manchester','Bristol','2025-02-14','2025-02-14','13:20:00','14:20:00',80),(6,'Bristol','London','2025-03-03','2025-03-03','07:40:00','08:20:00',80),(7,'London','Manchester','2025-03-17','2025-03-17','13:00:00','14:00:00',100),(8,'Manchester','Glasgow','2025-04-02','2025-04-02','12:20:00','13:30:00',100),(9,'Bristol','Glasgow','2025-04-10','2025-04-10','08:40:00','09:45:00',110),(10,'Glasgow','Newcastle','2025-04-20','2025-04-20','14:30:00','15:45:00',100),(11,'Newcastle','Manchester','2025-04-28','2025-04-28','16:15:00','17:05:00',100),(12,'Manchester','Bristol','2025-05-02','2025-05-02','18:25:00','19:30:00',80),(13,'Bristol','Manchester','2025-05-06','2025-05-06','06:20:00','07:20:00',80),(14,'Portsmouth','Dundee','2025-05-10','2025-05-10','12:00:00','14:00:00',120),(15,'Dundee','Portsmouth','2025-05-15','2025-05-15','10:00:00','12:00:00',120),(16,'Edinburgh','Cardiff','2025-05-20','2025-05-20','18:30:00','20:00:00',90),(17,'Southampton','Manchester','2025-05-25','2025-05-25','12:00:00','13:30:00',90),(18,'Manchester','Southampton','2025-05-29','2025-05-29','19:00:00','20:30:00',90),(19,'Birmingham','Newcastle','2025-06-01','2025-06-01','17:00:00','17:45:00',100),(20,'Newcastle','Birmingham','2025-06-05','2025-06-05','07:00:00','07:45:00',100),(21,'Aberdeen','Portsmouth','2025-06-10','2025-06-10','08:00:00','09:30:00',100),(22,'London','Bristol','2025-06-15','2025-06-15','13:30:00','14:10:00',80),(23,'Glasgow','Bristol','2025-06-20','2025-06-20','10:00:00','11:15:00',110),(24,'Manchester','London','2025-06-25','2025-06-25','09:30:00','10:30:00',100),(25,'Edinburgh','Glasgow','2025-06-30','2025-06-30','12:00:00','12:45:00',90),(26,'Newcastle','Cardiff','2025-07-05','2025-07-05','08:00:00','09:45:00',100),(27,'Bristol','Birmingham','2025-07-10','2025-07-10','15:30:00','16:15:00',90),(28,'Manchester','Edinburgh','2025-07-15','2025-07-15','10:30:00','11:45:00',100),(29,'Glasgow','London','2025-07-20','2025-07-20','09:00:00','10:30:00',100),(30,'London','Newcastle','2025-07-23','2025-07-23','14:00:00','15:15:00',100),(31,'Cardiff','Bristol','2025-08-01','2025-08-01','11:00:00','11:45:00',90),(32,'Portsmouth','Manchester','2025-08-05','2025-08-05','15:00:00','16:30:00',100),(33,'Dundee','Edinburgh','2025-08-10','2025-08-10','09:00:00','09:45:00',90),(34,'Birmingham','London','2025-05-12','2025-05-12','10:00:00','10:45:00',90),(35,'Glasgow','Edinburgh','2025-05-14','2025-05-14','13:00:00','13:45:00',90),(36,'Manchester','Birmingham','2025-05-16','2025-05-16','17:00:00','17:45:00',90),(37,'Newcastle','London','2025-05-17','2025-05-17','10:00:00','11:15:00',100),(38,'Cardiff','Glasgow','2025-05-18','2025-05-18','14:00:00','15:30:00',100),(39,'London','Edinburgh','2025-05-26','2025-05-26','09:00:00','10:30:00',100),(40,'Bristol','Cardiff','2025-12-24','2025-12-24','14:00:00','14:45:00',90),(41,'London','Manchester','2025-05-15','2025-05-15','07:00:00','08:00:00',100),(42,'London','Manchester','2025-05-15','2025-05-15','09:30:00','10:30:00',100),(43,'Manchester','London','2025-05-15','2025-05-15','06:30:00','07:30:00',100),(44,'Edinburgh','Cardiff','2025-05-17','2025-05-17','08:45:00','10:15:00',110),(45,'Bristol','Glasgow','2025-06-10','2025-06-10','06:45:00','08:00:00',110),(46,'Glasgow','Bristol','2025-06-10','2025-06-10','07:30:00','08:45:00',110);
/*!40000 ALTER TABLE `journey_details` ENABLE KEYS */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `Pay_ID` int NOT NULL AUTO_INCREMENT,
  `payment_amount` float NOT NULL,
  `receipt_number` varchar(45) NOT NULL,
  `pay_status` enum('unactive','Confirmed','Cancelled') NOT NULL,
  PRIMARY KEY (`Pay_ID`),
  UNIQUE KEY `receipt_number_UNIQUE` (`receipt_number`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,200,'v6DIyedz','Confirmed'),(2,99,'y4COupcq','Confirmed'),(3,81,'kMSWLZYX','Confirmed'),(4,180,'EiHEFvj1','Confirmed'),(5,180,'laZQUJQc','Confirmed'),(6,100,'z1I3npYy','Confirmed'),(7,200,'4Cj3Twu9','Confirmed'),(8,1000,'XSwDZ2oc','Confirmed');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;

--
-- Table structure for table `seats`
--

DROP TABLE IF EXISTS `seats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seats` (
  `Journey_ID` int NOT NULL,
  `economy_seats` int NOT NULL DEFAULT '104',
  `business_seats` int NOT NULL DEFAULT '26',
  KEY `seats_ibfk_1_idx` (`Journey_ID`),
  CONSTRAINT `seats_ibfk_1` FOREIGN KEY (`Journey_ID`) REFERENCES `journey` (`Journey_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seats`
--

/*!40000 ALTER TABLE `seats` DISABLE KEYS */;
INSERT INTO `seats` VALUES (1,103,26),(2,104,26),(3,104,26),(4,104,26),(5,104,26),(6,104,26),(7,104,26),(8,104,26),(9,104,26),(10,104,26),(11,104,26),(12,104,26),(13,104,26),(14,104,26),(15,104,26),(16,104,26),(17,104,26),(18,104,25),(19,104,25),(20,104,26),(21,104,26),(22,104,26),(23,104,26),(24,104,26),(25,104,26),(26,104,26),(27,104,26),(28,104,26),(29,104,26),(30,104,26),(31,104,26),(32,104,26),(33,104,26),(34,104,25),(35,104,26),(36,104,26),(37,104,26),(38,104,25),(39,104,26),(40,104,26),(41,103,26),(42,104,21),(43,104,26),(44,104,26),(45,103,26),(46,104,26);
/*!40000 ALTER TABLE `seats` ENABLE KEYS */;

--
-- Table structure for table `TravelCO`
--

DROP TABLE IF EXISTS `TravelCO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TravelCO` (
  `Tco_ID` int NOT NULL AUTO_INCREMENT,
  `Co_name` varchar(150) NOT NULL,
  PRIMARY KEY (`Tco_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TravelCO`
--

/*!40000 ALTER TABLE `TravelCO` DISABLE KEYS */;
INSERT INTO `TravelCO` VALUES (1,'AirExpress'),(2,'SkyWings'),(3,'JetStream'),(4,'MetroAir'),(5,'SkyLink'),(6,'AirNova'),(7,'WingJet'),(8,'HorizonAir'),(9,'SkyTravel'),(10,'AirScot');
/*!40000 ALTER TABLE `TravelCO` ENABLE KEYS */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_ID` int NOT NULL AUTO_INCREMENT,
  `role_ID` int NOT NULL,
  PRIMARY KEY (`user_ID`),
  KEY `role_ID` (`role_ID`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_ID`) REFERENCES `users_role` (`role_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,1),(3,1),(4,1),(5,1),(6,1),(1,2);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

--
-- Table structure for table `users_details`
--

DROP TABLE IF EXISTS `users_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_details` (
  `user_ID` int NOT NULL,
  `f_name` varchar(50) NOT NULL,
  `l_name` varchar(50) NOT NULL,
  `tel_number` varchar(15) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  KEY `user_ID` (`user_ID`),
  CONSTRAINT `users_details_ibfk_1` FOREIGN KEY (`user_ID`) REFERENCES `users` (`user_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_details`
--

/*!40000 ALTER TABLE `users_details` DISABLE KEYS */;
INSERT INTO `users_details` VALUES (1,'Admin','first','07000000000','admin@yahoo.com','$2b$12$PRy.1ckSBOBcX7XAhprG.OQ5T8LwYpjEf9bmnEhXRAVRN3rHbGzt6'),(2,'mohamed','hamouda','07234524434','mohamedhamouda1267@yahoo.com','$2b$12$Xaeawl4Aa7iwKINRuihG8eoiCFtkKfBUgmuyrQpXIxMSkTuZTADTO'),(3,'sarah','smith','07987673843','sarah_simth@yahoo.com','$2b$12$GoNWk9j88EdPef7o03kHTOfB260MmOL/YBoE9Tzb4qKE2NCIAfF2K'),(4,'john','doe','07833243243','john123@yahoo.com','$2b$12$h6hjU1rBUSNgFnUy3jaINeeY4Uc/bT4v2ISjEXZXlSmvScVffiFTm'),(5,'mark','john','07623243434','mark123@yahoo.com','$2b$12$21eP8ySR6qTpuH3Dy9OvjeEGsUEJdogf8OCM06UNsngDE8EyOVnVe'),(6,'john','brown','07986567876','brown9090@yahoo.com','$2b$12$gwS8Gj0wXq6d2bkug2A6Z.fnLicdcXyr7aKMHDk4DVXCSZo/vPEnW');
/*!40000 ALTER TABLE `users_details` ENABLE KEYS */;

--
-- Table structure for table `users_role`
--

DROP TABLE IF EXISTS `users_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_role` (
  `role_ID` int NOT NULL AUTO_INCREMENT,
  `role` varchar(8) NOT NULL,
  PRIMARY KEY (`role_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_role`
--

/*!40000 ALTER TABLE `users_role` DISABLE KEYS */;
INSERT INTO `users_role` VALUES (1,'customer'),(2,'Admin');
/*!40000 ALTER TABLE `users_role` ENABLE KEYS */;

--
-- Dumping routines for database 'Horizon_travel'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-26  1:46:09

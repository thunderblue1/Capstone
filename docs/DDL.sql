-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: curious_books
-- ------------------------------------------------------
-- Server version	8.0.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `isbn_13` varchar(13) DEFAULT NULL,
  `publisher` varchar(255) DEFAULT NULL,
  `publication_date` date DEFAULT NULL,
  `language` varchar(10) DEFAULT 'en',
  `genre` varchar(100) DEFAULT NULL,
  `description` text,
  `page_count` int DEFAULT '0',
  `price` decimal(10,2) NOT NULL,
  `currency` varchar(5) DEFAULT 'USD',
  `stock_quantity` int DEFAULT '0',
  `cover_image_url` varchar(500) DEFAULT NULL,
  `popularity_score` float DEFAULT '0',
  `average_rating` float DEFAULT '0',
  `review_count` int DEFAULT '0',
  `category_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `isbn_13` (`isbn_13`),
  KEY `category_id` (`category_id`),
  KEY `idx_books_title` (`title`),
  KEY `idx_books_genre` (`genre`),
  KEY `idx_books_author` (`author`),
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'The AI Revolution','Jane Doe','9781234567897','TechBooks Press','2024-03-15','en','Technology','Exploring how AI is reshaping business and science.',320,24.99,'USD',117,'ai_revolution.png',0,3.05555,9,1,'2025-11-07 14:03:51','2026-08-05 21:19:50'),(2,'Deep Learning Demystified','Alan Smith','9789876543210','NeuralPub','2023-09-10','en','Technology','A clear and practical introduction to deep learning.',410,29.99,'USD',79,'deep_learning.png',0,2.625,8,1,'2025-11-07 14:03:51','2026-08-05 21:19:50'),(3,'AI in Business','Sara Kim','9781122334455','BizBooks','2022-11-20','en','Business','How companies adopt AI to gain competitive advantage.',270,21.99,'USD',93,'ai_business.png',0,4.9,2,3,'2025-11-07 14:03:51','2026-07-30 05:39:12'),(4,'The Galactic Mystery','Tom Reed','9789988776655','StarLight Press','2021-05-10','en','Fiction','A thrilling sci-fi journey through space and time.',360,17.50,'USD',199,'galactic_mystery.png',0,4.21875,96,2,'2025-11-07 14:03:51','2026-08-05 21:19:50'),(5,'Little Inventors','Lily Brown','9784433221100','KidsWorld','2020-08-01','en','Children','Inspiring stories for young inventors and dreamers.',150,12.99,'USD',299,'little_inventors.png',0,4.8,310,5,'2025-11-07 14:03:51','2026-07-23 15:58:35'),(6,'Quantum Reality: The New Physics','Dr. Aris Thorne','9781100223344','Nova Science','2023-11-12','en','Science','A deep dive into the paradoxical world of quantum mechanics.',390,34.99,'USD',142,'quantum_reality.png',0,4.69697,198,4,'2026-07-23 16:17:33','2026-08-05 21:19:50'),(7,'The Midnight Cipher','Eleanor Vance','9780091234567','Obsidian Ink','2024-01-20','en','Fiction','An old book code unlocks a centuries-old London mystery.',315,19.99,'USD',87,'midnight_cipher.png',0,4.5,116,2,'2026-07-23 16:17:33','2026-08-05 21:19:50'),(8,'The Dragon\'s Apprentice','Oliver Swift','9784400556677','StoryTime Press','2022-06-15','en','Children','A young boy learns magic and friendship from an unlikely mentor.',180,14.50,'USD',210,'dragons_apprentice.png',0,4.8,340,8,'2026-07-23 16:17:33','2026-07-23 16:18:29'),(9,'Python for Tomorrow: AI & Data Science','Kenji Tanaka','9781188990011','CodeHorizon','2024-05-01','en','Technology','Advanced Python techniques for AI and modern data processing.',450,45.00,'USD',65,'python_tomorrow.png',0,4.9,85,1,'2026-07-23 16:17:33','2026-07-23 16:18:29'),(10,'StartUp: From Idea to IPO','Maria Garcia','9780800778899','Venture Books','2023-08-10','en','Business','The complete roadmap for launching and scaling a high-growth startup.',300,27.99,'USD',119,'startup_ipo.png',0,4.6,160,3,'2026-07-23 16:17:33','2026-07-24 20:57:52'),(11,'The Stardust Chronicles','J.R. Sterling','9789900112233','Galactic Teens','2024-02-14','en','Young Adult','A group of teens navigates love and survival on a distant space colony.',330,18.99,'USD',175,'stardust_chronicles.png',0,4.3,210,5,'2026-07-23 16:17:33','2026-07-23 16:18:29'),(12,'Ancient Oceans: Prehistoric Marine Life','Dr. Sarah Chen','9783300445566','Terra Nautilus','2023-10-05','en','Nonfiction','Exploring the bizarre and massive creatures that ruled Earth\'s seas.',280,29.99,'USD',95,'ancient_oceans.png',0,4.69097,144,7,'2026-07-23 16:17:33','2026-08-05 21:19:50'),(13,'Digital Minimalism: Finding Focus','Cal Newport','9781100998877','Mindful Living','2022-09-01','en','Adult','A philosophy of technology use to improve focus and well-being.',250,22.00,'USD',310,'digital_minimalism.png',0,4.8,520,6,'2026-07-23 16:17:33','2026-07-23 16:18:29'),(14,'Robotic Futures: The Automation Age','David Lee','9785500667788','FutureTech','2024-04-10','en','Technology','The technology and ethics of robotics in the next decade.',310,31.50,'USD',49,'robotic_futures.png',0,4.4,75,1,'2026-07-23 16:17:33','2026-07-24 20:57:52'),(15,'The Silent Planet','C.S. Lewis','9788800110022','Cosmos Classics','2021-12-01','en','Fiction','A philologist is abducted and taken to a mysterious, vibrant Mars.',220,15.99,'USD',205,'silent_planet.png',0,4.50164,305,2,'2026-07-23 16:17:33','2026-08-05 21:19:50');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `parent_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_category_parent` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Technology',NULL),(2,'Fiction',NULL),(3,'Business',NULL),(4,'Science',NULL),(5,'Young Adult',NULL),(6,'Adult',NULL),(7,'Nonfiction',NULL),(8,'Children',NULL);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `book_id` int NOT NULL,
  `quantity` int DEFAULT '1',
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `idx_orderitems_book` (`book_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,1,24.99),(2,1,3,1,21.99),(3,2,4,1,17.50),(4,3,1,2,24.99),(5,4,3,1,21.99),(6,4,5,1,12.99),(7,4,1,1,24.99),(8,5,2,1,29.99),(9,5,4,1,17.50),(10,6,7,1,19.99),(11,7,14,1,31.50),(12,7,10,1,27.99),(13,8,3,1,21.99),(14,9,4,1,17.50),(15,10,4,1,17.50),(16,11,4,1,17.50),(17,12,4,1,17.50),(18,13,4,1,17.50),(19,14,4,1,17.50);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `currency` varchar(5) DEFAULT 'USD',
  `status` enum('Pending','Paid','Shipped','Delivered','Cancelled') DEFAULT 'Pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `stripe_payment_intent_id` varchar(255) DEFAULT NULL,
  `stripe_customer_id` varchar(255) DEFAULT NULL,
  `customer_email` varchar(150) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `shipping_address_line1` varchar(255) DEFAULT NULL,
  `shipping_address_line2` varchar(255) DEFAULT NULL,
  `shipping_city` varchar(100) DEFAULT NULL,
  `shipping_state` varchar(50) DEFAULT NULL,
  `shipping_postal_code` varchar(20) DEFAULT NULL,
  `shipping_country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_orders_user` (`user_id`),
  KEY `idx_stripe_payment_intent_id` (`stripe_payment_intent_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,46.98,'USD','Paid','2025-11-07 14:03:51','2025-11-07 14:03:51',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,2,17.50,'USD','Pending','2025-11-07 14:03:51','2025-11-07 14:03:51',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,5,53.98,'USD','Paid','2026-01-01 23:26:52','2026-01-01 23:26:52','pi_3SkvGQKTQjdI7Mup09OVIIvb','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(4,5,59.97,'USD','Paid','2026-01-20 16:34:20','2026-01-20 16:34:20','pi_3SrhsQKTQjdI7Mup1or3DjQ1','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(5,5,47.49,'USD','Paid','2026-01-20 17:17:50','2026-01-20 17:17:50','pi_3SriYgKTQjdI7Mup07dxm1qo','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(6,7,19.99,'USD','Paid','2026-07-24 20:40:30','2026-07-24 20:40:30','pi_3TwpsmKTQjdI7Mup0wJHrMPF','cus_UwjLU9Hd8cHA4C','blueisgoodtoo@gmail.com','Blue Tech LLC','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(7,5,59.49,'USD','Paid','2026-07-24 20:57:52','2026-07-24 20:57:52','pi_3TwqA0KTQjdI7Mup1eeb1bV6','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','234 sdfg','','Redmond','OR','97756','US'),(8,5,21.99,'USD','Paid','2026-07-30 05:39:12','2026-07-30 05:39:12','pi_3TymfuKTQjdI7Mup1eOBBw8O','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John Keen','4703 Northeast Butler Avenue','','Redmond','OR','97756','US'),(9,8,17.50,'USD','Paid','2026-08-05 21:19:49','2026-08-05 21:19:49',NULL,NULL,'user01@cf-demo.curiousbooks.local','Casey FictionFan',NULL,NULL,NULL,NULL,NULL,NULL),(10,9,17.50,'USD','Paid','2026-08-05 21:19:50','2026-08-05 21:19:50',NULL,NULL,'user02@cf-demo.curiousbooks.local','Jordan StoryLover',NULL,NULL,NULL,NULL,NULL,NULL),(11,10,17.50,'USD','Paid','2026-08-05 21:19:50','2026-08-05 21:19:50',NULL,NULL,'user03@cf-demo.curiousbooks.local','Riley NovelReader',NULL,NULL,NULL,NULL,NULL,NULL),(12,11,17.50,'USD','Paid','2026-08-05 21:19:50','2026-08-05 21:19:50',NULL,NULL,'user04@cf-demo.curiousbooks.local','Avery ScienceBuff',NULL,NULL,NULL,NULL,NULL,NULL),(13,12,17.50,'USD','Paid','2026-08-05 21:19:50','2026-08-05 21:19:50',NULL,NULL,'user05@cf-demo.curiousbooks.local','Morgan FactFinder',NULL,NULL,NULL,NULL,NULL,NULL),(14,13,17.50,'USD','Paid','2026-08-05 21:19:50','2026-08-05 21:19:50',NULL,NULL,'user06@cf-demo.curiousbooks.local','Quinn MixedTaste',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `rating` float DEFAULT NULL,
  `comment` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_reviews_book` (`book_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_chk_1` CHECK (((`rating` >= 0) and (`rating` <= 5)))
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,1,5,'Fascinating and insightful!','2025-11-07 14:03:51'),(2,2,1,4.5,'Great overview of AI trends.','2025-11-07 14:03:51'),(3,3,2,4,'Good explanations but a bit dense.','2025-11-07 14:03:51'),(4,1,3,4.8,'Perfect for entrepreneurs!','2025-11-07 14:03:51'),(5,5,3,5,'I love this book!  I wish I could read it with a clear mind and not distracted.','2025-12-11 04:43:52'),(6,5,2,4,'This is a good book but I don\'t feel well and want to only give it a 3.','2026-07-24 20:50:19'),(7,5,1,5,'I am having a better day and like this book in this moment.','2026-07-24 20:59:33'),(8,8,4,5,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(9,8,7,5,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(10,8,12,5,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(11,8,15,5,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(12,8,1,2,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(13,8,2,2,'Demo CF seed rating (cf_demo_user_01)','2026-08-05 21:19:49'),(14,9,4,4.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(15,9,7,4.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(16,9,12,4.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(17,9,15,4.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(18,9,1,2.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(19,9,2,2.5,'Demo CF seed rating (cf_demo_user_02)','2026-08-05 21:19:50'),(20,10,4,4,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(21,10,7,4,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(22,10,12,4,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(23,10,15,4,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(24,10,1,1.5,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(25,10,2,1.5,'Demo CF seed rating (cf_demo_user_03)','2026-08-05 21:19:50'),(26,11,4,5,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(27,11,6,5,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(28,11,7,5,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(29,11,15,5,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(30,11,1,2,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(31,11,2,2,'Demo CF seed rating (cf_demo_user_04)','2026-08-05 21:19:50'),(32,12,4,4.5,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(33,12,6,4.5,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(34,12,7,4.5,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(35,12,15,4.5,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(36,12,1,2,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(37,12,2,2,'Demo CF seed rating (cf_demo_user_05)','2026-08-05 21:19:50'),(38,13,4,4,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50'),(39,13,6,4,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50'),(40,13,7,4,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50'),(41,13,12,4,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50'),(42,13,1,3,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50'),(43,13,2,3,'Demo CF seed rating (cf_demo_user_06)','2026-08-05 21:19:50');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blocklist`
--

DROP TABLE IF EXISTS `token_blocklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blocklist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jti` varchar(36) NOT NULL,
  `type` varchar(16) NOT NULL,
  `exp` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_token_blocklist_jti` (`jti`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blocklist`
--

LOCK TABLES `token_blocklist` WRITE;
/*!40000 ALTER TABLE `token_blocklist` DISABLE KEYS */;
INSERT INTO `token_blocklist` VALUES (1,'6141c05c-1a33-47e1-b3b6-1be2fe32b469','refresh','2026-09-22 20:48:32','2026-07-24 20:48:49');
/*!40000 ALTER TABLE `token_blocklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'customer',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_users_role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Wonderland Alice','alice@example.com','hashed_pw_1','2025-11-07 14:03:51','Alice','Beguile','customer'),(2,'Big O Bob','bob@example.com','hashed_pw_2','2025-11-07 14:03:51','Bob','Boodock','customer'),(3,'Kickin\' it Carol','carol@example.com','hashed_pw_3','2025-11-07 14:03:51','Carol','joggington','customer'),(4,'Bald Guy','user@domain.com','password','2025-11-07 14:03:51','Johnny','Mnemonic','customer'),(5,'John','johnkeen.dev@gmail.com','scrypt:32768:8:1$AT3DcsOBxZEe86Dn$6a9685fa2795ce73248282ff67f507e10e3979016e2a902594ffb9a0135685c9c2bb6aa4469f8d5d1b7ba6eef8e8a71e7c3f55455dd4bd4ef725e51f0c153c80','2025-12-11 04:25:47','John','Keen','manager'),(7,'Blue Tech LLC','blueisgoodtoo@gmail.com','scrypt:32768:8:1$DlK7gAHDFyuonRP5$10b38657bfd403c9d4ebc20fdbeeba0d0ca9bc897ef15a4496a287f98dd617f9a586dfffc180cf25cd50e615d1a36c9f7d63882a3419fb02d687861ee1e2bdd9','2026-07-24 20:38:15',NULL,NULL,'customer'),(8,'cf_demo_user_01','user01@cf-demo.curiousbooks.local','scrypt:32768:8:1$1TzFP91IQ6Fbgd2D$017961211c7a3c2b1b997716aea78104d9d6a1a2384c21e13a6b100ad55f9cd20af2908c9fc43e5e364189017dc6c91c6c3ed48e38c761eb453be24aef42ef5e','2026-08-05 21:19:49','Casey','FictionFan','customer'),(9,'cf_demo_user_02','user02@cf-demo.curiousbooks.local','scrypt:32768:8:1$binL32EecZwqJKED$f658492e7b12e9cdec1af76874a35ba13777cf0c19d0eb8b167fac4aa9c27da9ab897adf257266f52fb25ab703920feaae796705505dc8998add23d7072d2d25','2026-08-05 21:19:49','Jordan','StoryLover','customer'),(10,'cf_demo_user_03','user03@cf-demo.curiousbooks.local','scrypt:32768:8:1$sDApgiQFHtbJIolJ$f5d53aeaddf442c433f4b876d04dd6311ebf76ca0085066d656c4992d5897b0b4e35efd2409f1ab9ed8b37f1d21cae56fd0c36d4043911eacfd900aa18defea5','2026-08-05 21:19:49','Riley','NovelReader','customer'),(11,'cf_demo_user_04','user04@cf-demo.curiousbooks.local','scrypt:32768:8:1$3ofgvpj7kDUuikyU$3754dd50b22eb833eec4034e106188fbc680bc7dfa10cda2fef0a2c3c204d1f5bee681dacf7fbffaeaca8a61b329d5511c14a9550c0659efc3b4c11b7a5bbe79','2026-08-05 21:19:49','Avery','ScienceBuff','customer'),(12,'cf_demo_user_05','user05@cf-demo.curiousbooks.local','scrypt:32768:8:1$DZCNmg25tKhynpWs$91f56fea183320ce5a76e527ddb9f827968a0e0b2f28a91bf574864d73965320c4492782170bff1b8db3f2be47e9f83be0ae29d91a5a85be9f70b4a237f483d7','2026-08-05 21:19:49','Morgan','FactFinder','customer'),(13,'cf_demo_user_06','user06@cf-demo.curiousbooks.local','scrypt:32768:8:1$RWJpsFydvXVVv6JB$71d94331bf754f831db011c2fa437e0506586396e84c03da1a97189bc25eadc289cef47f51c61e8d59b28eeaa21354d6043548fec2089abd12fac64f6aaaeff5','2026-08-05 21:19:49','Quinn','MixedTaste','customer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'curious_books'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-07 16:26:54

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'The AI Revolution','Jane Doe','9781234567897','TechBooks Press','2024-03-15','en','Technology','Exploring how AI is reshaping business and science.',320,24.99,'USD',117,'ai-revolution.jpg',0,4.6,250,1,'2025-11-07 14:03:51','2026-01-20 16:34:20'),(2,'Deep Learning Demystified','Alan Smith','9789876543210','NeuralPub','2023-09-10','en','Technology','A clear and practical introduction to deep learning.',410,29.99,'USD',79,'deep-learning.jpg',0,4.4,180,1,'2025-11-07 14:03:51','2026-01-20 17:17:50'),(3,'AI in Business','Sara Kim','9781122334455','BizBooks','2022-11-20','en','Business','How companies adopt AI to gain competitive advantage.',270,21.99,'USD',94,'ai-business.jpg',0,4.9,2,3,'2025-11-07 14:03:51','2026-01-20 16:34:20'),(4,'The Galactic Mystery','Tom Reed','9789988776655','StarLight Press','2021-05-10','en','Fiction','A thrilling sci-fi journey through space and time.',360,17.50,'USD',199,'galactic-mystery.jpg',0,4.2,90,2,'2025-11-07 14:03:51','2026-01-20 17:17:50'),(5,'Little Inventors','Lily Brown','9784433221100','KidsWorld','2020-08-01','en','Children','Inspiring stories for young inventors and dreamers.',150,12.99,'USD',299,'little-inventors.jpg',0,4.8,310,5,'2025-11-07 14:03:51','2026-01-20 16:34:20');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,1,1,24.99),(2,1,3,1,21.99),(3,2,4,1,17.50),(4,3,1,2,24.99),(5,4,3,1,21.99),(6,4,5,1,12.99),(7,4,1,1,24.99),(8,5,2,1,29.99),(9,5,4,1,17.50);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,46.98,'USD','Paid','2025-11-07 14:03:51','2025-11-07 14:03:51',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(2,2,17.50,'USD','Pending','2025-11-07 14:03:51','2025-11-07 14:03:51',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,5,53.98,'USD','Paid','2026-01-01 23:26:52','2026-01-01 23:26:52','pi_3SkvGQKTQjdI7Mup09OVIIvb','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(4,5,59.97,'USD','Paid','2026-01-20 16:34:20','2026-01-20 16:34:20','pi_3SrhsQKTQjdI7Mup1or3DjQ1','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US'),(5,5,47.49,'USD','Paid','2026-01-20 17:17:50','2026-01-20 17:17:50','pi_3SriYgKTQjdI7Mup07dxm1qo','cus_TiLUZDa8HO72LO','johnkeen.dev@gmail.com','John','4703 NE Butler Avenue','','Redmond','OR','97756','US');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,1,5,'Fascinating and insightful!','2025-11-07 14:03:51'),(2,2,1,4.5,'Great overview of AI trends.','2025-11-07 14:03:51'),(3,3,2,4,'Good explanations but a bit dense.','2025-11-07 14:03:51'),(4,1,3,4.8,'Perfect for entrepreneurs!','2025-11-07 14:03:51'),(5,5,3,5,'I love this book!  I wish I could read it with a clear mind and not distracted.','2025-12-11 04:43:52');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Wonderland Alice','alice@example.com','hashed_pw_1','2025-11-07 14:03:51','Alice','Beguile','customer'),(2,'Big O Bob','bob@example.com','hashed_pw_2','2025-11-07 14:03:51','Bob','Boodock','customer'),(3,'Kickin\' it Carol','carol@example.com','hashed_pw_3','2025-11-07 14:03:51','Carol','joggington','customer'),(4,'Bald Guy','user@domain.com','password','2025-11-07 14:03:51','Johnny','Mnemonic','customer'),(5,'John','johnkeen.dev@gmail.com','scrypt:32768:8:1$AT3DcsOBxZEe86Dn$6a9685fa2795ce73248282ff67f507e10e3979016e2a902594ffb9a0135685c9c2bb6aa4469f8d5d1b7ba6eef8e8a71e7c3f55455dd4bd4ef725e51f0c153c80','2025-12-11 04:25:47',NULL,NULL,'manager');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
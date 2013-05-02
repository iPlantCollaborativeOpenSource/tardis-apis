-- MySQL dump 10.13  Distrib 5.6.10, for osx10.7 (x86_64)
--
-- Host: localhost    Database: provenance
-- ------------------------------------------------------
-- Server version	5.6.10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Audit`
--

DROP TABLE IF EXISTS `Audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Audit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` bigint(20) NOT NULL,
  `service_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `username` varchar(30) CHARACTER SET latin1 NOT NULL,
  `proxy_username` varchar(30) CHARACTER SET latin1 DEFAULT NULL,
  `event_data` varchar(75) CHARACTER SET latin1 DEFAULT NULL,
  `request_ipaddress` varchar(39) CHARACTER SET latin1 NOT NULL,
  `created_date` int(11) NOT NULL,
  `processed` varchar(5) CHARACTER SET latin1 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Category`
--

DROP TABLE IF EXISTS `Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Category` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(128) CHARACTER SET latin1 NOT NULL,
  `category_desc` varchar(255) CHARACTER SET latin1 DEFAULT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Event`
--

DROP TABLE IF EXISTS `Event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Event` (
  `event_id` int(11) NOT NULL AUTO_INCREMENT,
  `event_name` varchar(128) CHARACTER SET latin1 NOT NULL,
  `event_desc` varchar(255) CHARACTER SET latin1 DEFAULT NULL,
  PRIMARY KEY (`event_id`)
) ENGINE=MyISAM AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `History`
--

DROP TABLE IF EXISTS `History`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `History` (
  `history_id` int(11) NOT NULL AUTO_INCREMENT,
  `provenance_id` int(11) NOT NULL,
  `provenance_parent_id` int(11) NOT NULL,
  PRIMARY KEY (`history_id`),
  KEY `provenance_id` (`provenance_id`),
  KEY `provenance_parent_id` (`provenance_parent_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Object`
--

DROP TABLE IF EXISTS `Object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Object` (
  `id` int(11) NOT NULL DEFAULT '0',
  `uuid` bigint(20) NOT NULL,
  `service_id` int(11) NOT NULL DEFAULT '0',
  `object_id` varchar(128) NOT NULL DEFAULT '',
  `object_name` varchar(128) CHARACTER SET latin1 DEFAULT NULL,
  `object_desc` varchar(355) CHARACTER SET latin1 DEFAULT NULL,
  `parent_uuid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`service_id`,`object_id`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Provenance`
--

DROP TABLE IF EXISTS `Provenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Provenance` (
  `provenance_id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` bigint(20) NOT NULL,
  `event_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `username` varchar(30) CHARACTER SET latin1 NOT NULL,
  `proxy_username` varchar(30) CHARACTER SET latin1 DEFAULT NULL,
  `request_ipaddress` varchar(39) CHARACTER SET latin1 DEFAULT NULL,
  `event_data` varchar(1024) CHARACTER SET latin1 DEFAULT NULL,
  `created_date` int(11) NOT NULL,
  PRIMARY KEY (`provenance_id`),
  KEY `uuid` (`uuid`),
  KEY `service_id` (`service_id`),
  KEY `category_id` (`category_id`),
  KEY `event_id` (`event_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Service`
--

DROP TABLE IF EXISTS `Service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Service` (
  `service_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_key` varchar(10) NOT NULL,
  `service_name` varchar(128) CHARACTER SET latin1 NOT NULL,
  `service_desc` varchar(255) CHARACTER SET latin1 DEFAULT NULL,
  `service_link` varchar(1024) CHARACTER SET latin1 DEFAULT NULL,
  `service_ipaddress` varchar(39) CHARACTER SET latin1 DEFAULT NULL,
  `service_group` varchar(64) CHARACTER SET latin1 NOT NULL,
  `service_type` varchar(10) NOT NULL,
  `service_version` varchar(10) NOT NULL,
  `version_status` char(1) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT 'I',
  PRIMARY KEY (`service_id`),
  UNIQUE KEY `cons_service_key` (`service_key`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `history_requests`
--

DROP TABLE IF EXISTS `history_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `history_code` varchar(70) CHARACTER SET latin1 NOT NULL,
  `uuid` bigint(20) NOT NULL,
  `service_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `username` varchar(30) CHARACTER SET latin1 NOT NULL,
  `created_date` int(11) NOT NULL,
  `parent` varchar(5) CHARACTER SET latin1 NOT NULL DEFAULT 'N',
  `processed` varchar(5) CHARACTER SET latin1 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-05-01 18:13:56

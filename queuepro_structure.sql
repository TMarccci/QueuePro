-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 11, 2023 at 07:27 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.0.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `queuepro`
--
CREATE DATABASE IF NOT EXISTS `queuepro` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `queuepro`;

-- --------------------------------------------------------

--
-- Table structure for table `qp_sessionmusics`
--

DROP TABLE IF EXISTS `qp_sessionmusics`;
CREATE TABLE IF NOT EXISTS `qp_sessionmusics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `whichsession` varchar(255) DEFAULT NULL,
  `sentbywhoid` varchar(255) DEFAULT NULL,
  `url` varchar(5000) DEFAULT NULL,
  `placeinqueue` int(20) DEFAULT NULL,
  `isplaying` tinyint(1) DEFAULT NULL,
  `isplayed` tinyint(1) DEFAULT NULL,
  `ifplayedwhen` datetime DEFAULT NULL,
  `videoname` varchar(255) DEFAULT NULL,
  `videolenght` int(20) DEFAULT NULL,
  `thumbnailurl` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `whichsession` (`whichsession`),
  KEY `sentbywhoid` (`sentbywhoid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `qp_sessions`
--

DROP TABLE IF EXISTS `qp_sessions`;
CREATE TABLE IF NOT EXISTS `qp_sessions` (
  `sessionid` varchar(255) NOT NULL,
  `sessioncode` varchar(255) DEFAULT NULL,
  `skipsperuser` int(20) DEFAULT NULL,
  `timebetweensamemusic` int(20) DEFAULT NULL,
  `samemusicmaxtimes` int(20) DEFAULT NULL,
  `maxvideolenght` int(20) DEFAULT NULL,
  `creationdate` datetime DEFAULT NULL,
  `skipcurrent` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`sessionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `qp_sessionusers`
--

DROP TABLE IF EXISTS `qp_sessionusers`;
CREATE TABLE IF NOT EXISTS `qp_sessionusers` (
  `whichsession` varchar(255) DEFAULT NULL,
  `userid` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `skipsleft` int(20) DEFAULT NULL,
  `totalsongs` int(20) DEFAULT NULL,
  UNIQUE KEY `userid` (`userid`),
  KEY `whichsession` (`whichsession`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `qp_sessionmusics`
--
ALTER TABLE `qp_sessionmusics`
  ADD CONSTRAINT `qp_sessionmusics_ibfk_1` FOREIGN KEY (`whichsession`) REFERENCES `qp_sessions` (`sessionid`),
  ADD CONSTRAINT `qp_sessionmusics_ibfk_2` FOREIGN KEY (`sentbywhoid`) REFERENCES `qp_sessionusers` (`userid`);

--
-- Constraints for table `qp_sessionusers`
--
ALTER TABLE `qp_sessionusers`
  ADD CONSTRAINT `qp_sessionusers_ibfk_1` FOREIGN KEY (`whichsession`) REFERENCES `qp_sessions` (`sessionid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

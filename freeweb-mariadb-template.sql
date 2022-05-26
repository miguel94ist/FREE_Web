-- MariaDB dump 10.19  Distrib 10.5.15-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: freeweb
-- ------------------------------------------------------
-- Server version	10.6.5-MariaDB-1:10.6.5+maria~focal

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add result',7,'add_result'),(26,'Can change result',7,'change_result'),(27,'Can delete result',7,'delete_result'),(28,'Can view result',7,'view_result'),(29,'Can add Experiment',8,'add_experiment'),(30,'Can change Experiment',8,'change_experiment'),(31,'Can delete Experiment',8,'delete_experiment'),(32,'Can view Experiment',8,'view_experiment'),(33,'Can add status',9,'add_status'),(34,'Can change status',9,'change_status'),(35,'Can delete status',9,'delete_status'),(36,'Can view status',9,'view_status'),(37,'Can add Experimental apparatus',10,'add_apparatus'),(38,'Can change Experimental apparatus',10,'change_apparatus'),(39,'Can delete Experimental apparatus',10,'delete_apparatus'),(40,'Can view Experimental apparatus',10,'view_apparatus'),(41,'Can add Experimental protocol',11,'add_protocol'),(42,'Can change Experimental protocol',11,'change_protocol'),(43,'Can delete Experimental protocol',11,'delete_protocol'),(44,'Can view Experimental protocol',11,'view_protocol'),(45,'Can add Protocol execution',12,'add_execution'),(46,'Can change Protocol execution',12,'change_execution'),(47,'Can delete Protocol execution',12,'delete_execution'),(48,'Can view Protocol execution',12,'view_execution'),(49,'Can add user profile',13,'add_userprofile'),(50,'Can change user profile',13,'change_userprofile'),(51,'Can delete user profile',13,'delete_userprofile'),(52,'Can view user profile',13,'view_userprofile'),(53,'Can add attachment',14,'add_attachment'),(54,'Can change attachment',14,'change_attachment'),(55,'Can delete attachment',14,'delete_attachment'),(56,'Can view attachment',14,'view_attachment'),(57,'Can add ApparatusType',8,'add_apparatustype'),(58,'Can change ApparatusType',8,'change_apparatustype'),(59,'Can delete ApparatusType',8,'delete_apparatustype'),(60,'Can view ApparatusType',8,'view_apparatustype'),(61,'Can add association',15,'add_association'),(62,'Can change association',15,'change_association'),(63,'Can delete association',15,'delete_association'),(64,'Can view association',15,'view_association'),(65,'Can add code',16,'add_code'),(66,'Can change code',16,'change_code'),(67,'Can delete code',16,'delete_code'),(68,'Can view code',16,'view_code'),(69,'Can add nonce',17,'add_nonce'),(70,'Can change nonce',17,'change_nonce'),(71,'Can delete nonce',17,'delete_nonce'),(72,'Can view nonce',17,'view_nonce'),(73,'Can add user social auth',18,'add_usersocialauth'),(74,'Can change user social auth',18,'change_usersocialauth'),(75,'Can delete user social auth',18,'delete_usersocialauth'),(76,'Can view user social auth',18,'view_usersocialauth'),(77,'Can add partial',19,'add_partial'),(78,'Can change partial',19,'change_partial'),(79,'Can delete partial',19,'delete_partial'),(80,'Can view partial',19,'view_partial');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (6,'pbkdf2_sha256$320000$OI6PcLLoNPFWIRJlUPrgDn$dBMrSUkGogl8PVIuU0qGrjvgtR2WYraXzOHQVdyFCMw=','2022-05-26 19:54:53.732036',1,'wp-admin','admin','istrator','',1,1,'2021-11-14 23:21:20.000000'),(7,'pbkdf2_sha256$320000$j1O7BHMwdW3cMroHJWqt0h$Oy/ZFtqYEIu/J+B4nKNKeBY3S0M2D8u7U3TBkNNdwk0=','2022-05-26 13:30:03.253942',0,'wpa','Guest','','',0,1,'2021-11-15 03:12:42.000000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=422 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(14,'django_summernote','attachment'),(10,'free','apparatus'),(8,'free','apparatustype'),(12,'free','execution'),(11,'free','protocol'),(7,'free','result'),(9,'free','status'),(13,'free','userprofile'),(6,'sessions','session'),(15,'social_django','association'),(16,'social_django','code'),(17,'social_django','nonce'),(19,'social_django','partial'),(18,'social_django','usersocialauth');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (26,'free','0002_auto_20210913_1719','2021-09-13 17:19:49.847998'),(28,'free','0003_auto_20210916_2049','2021-09-16 20:50:11.616598'),(35,'free','0008_auto_20211022_1415','2021-10-22 13:16:15.415760'),(75,'contenttypes','0001_initial','2022-05-19 21:11:47.871502'),(76,'auth','0001_initial','2022-05-19 21:11:47.883134'),(77,'admin','0001_initial','2022-05-19 21:11:47.892374'),(78,'admin','0002_logentry_remove_auto_add','2022-05-19 21:11:47.900241'),(79,'admin','0003_logentry_add_action_flag_choices','2022-05-19 21:11:47.908146');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_summernote_attachment`
--

DROP TABLE IF EXISTS `django_summernote_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_summernote_attachment` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `file` varchar(100) NOT NULL,
  `uploaded` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_summernote_attachment`
--

LOCK TABLES `django_summernote_attachment` WRITE;
/*!40000 ALTER TABLE `django_summernote_attachment` DISABLE KEYS */;
INSERT INTO `django_summernote_attachment` VALUES (1,'Centro Regional Chiriquí 2.png','django-summernote/2022-04-12/b97f9fd6-7af1-43e5-98b3-9ae08426968f.png','2022-04-12 21:09:27.921267'),(2,'Centro Regional Chiriquí 1.png','django-summernote/2022-04-12/c3f13125-a0cf-407c-9fa7-1a56b629108e.png','2022-04-12 21:10:05.741316');
/*!40000 ALTER TABLE `django_summernote_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_apparatus`
--

DROP TABLE IF EXISTS `free_apparatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_apparatus` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `secret` varchar(32) NOT NULL,
  `owner` varchar(32) NOT NULL,
  `location` varchar(64) NOT NULL,
  `location_en` varchar(64) DEFAULT NULL,
  `location_pt` varchar(64) DEFAULT NULL,
  `video_config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`video_config`)),
  `location_es` varchar(64) DEFAULT NULL,
  `config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`config`)),
  `timeout` int(11) NOT NULL,
  `description` longtext NOT NULL,
  `description_en` longtext DEFAULT NULL,
  `description_es` longtext DEFAULT NULL,
  `description_pt` longtext DEFAULT NULL,
  `apparatus_type_id` bigint(20) NOT NULL,
  `last_online` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `free_apparatus_apparatus_type_id_9a01e43f_fk_free_appa` (`apparatus_type_id`),
  CONSTRAINT `free_apparatus_apparatus_type_id_9a01e43f_fk_free_appa` FOREIGN KEY (`apparatus_type_id`) REFERENCES `free_apparatustype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_apparatus`
--

LOCK TABLES `free_apparatus` WRITE;
/*!40000 ALTER TABLE `free_apparatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `free_apparatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_apparatus_protocols`
--

DROP TABLE IF EXISTS `free_apparatus_protocols`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_apparatus_protocols` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `apparatus_id` bigint(20) NOT NULL,
  `protocol_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `free_apparatus_protocols_apparatus_id_protocol_id_03090a96_uniq` (`apparatus_id`,`protocol_id`),
  KEY `free_apparatus_proto_protocol_id_241bf2d7_fk_free_prot` (`protocol_id`),
  CONSTRAINT `free_apparatus_proto_apparatus_id_a2ef4b39_fk_free_appa` FOREIGN KEY (`apparatus_id`) REFERENCES `free_apparatus` (`id`),
  CONSTRAINT `free_apparatus_proto_protocol_id_241bf2d7_fk_free_prot` FOREIGN KEY (`protocol_id`) REFERENCES `free_protocol` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_apparatus_protocols`
--

LOCK TABLES `free_apparatus_protocols` WRITE;
/*!40000 ALTER TABLE `free_apparatus_protocols` DISABLE KEYS */;
/*!40000 ALTER TABLE `free_apparatus_protocols` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_apparatustype`
--

DROP TABLE IF EXISTS `free_apparatustype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_apparatustype` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `name_en` varchar(64) DEFAULT NULL,
  `name_pt` varchar(64) DEFAULT NULL,
  `description` longtext NOT NULL,
  `description_en` longtext DEFAULT NULL,
  `description_pt` longtext DEFAULT NULL,
  `scientific_area` varchar(64) NOT NULL,
  `scientific_area_en` varchar(64) DEFAULT NULL,
  `scientific_area_pt` varchar(64) DEFAULT NULL,
  `lab_type` varchar(32) NOT NULL,
  `lab_type_en` varchar(32) DEFAULT NULL,
  `lab_type_pt` varchar(32) DEFAULT NULL,
  `slug` varchar(64) NOT NULL,
  `description_es` longtext DEFAULT NULL,
  `lab_type_es` varchar(32) DEFAULT NULL,
  `name_es` varchar(64) DEFAULT NULL,
  `scientific_area_es` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `free_experiment_slug_df3b5056` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_apparatustype`
--

LOCK TABLES `free_apparatustype` WRITE;
/*!40000 ALTER TABLE `free_apparatustype` DISABLE KEYS */;
INSERT INTO `free_apparatustype` VALUES (1,'Pendulum','Pendulum','Pêndulo','<section class=\"intro\">\n\n                                    <p>This Experiment allows the study of the acceleration of gravity in different points of the globe. For this purpose, an observation of several pendulums placed at different latitudes and operated remotely over the internet can be used. <br> <br>However, other experimental protocols can be performed, not only in local gravity to fit a suitable geophysical model but also to study simple mechanical principles such as conservation of mechanical energy.<br><br></p>\n\n\n\n                                </section>\n\n                                <h3> Detalhes do pêndulo</h3>\n\n                                <p>Comprimento de cabo (sem contar com a esfera):<a href=\"https://groups.ist.utl.pt/wwwelab/wiki/index.php?title=P%C3%AAndulo_Mundial#Aparato_experimental\"><em>Verifique aqui para cada lugar</em></a></p>\n\n\n\n<table id=\"example_1\" class=\"ui celled padded table\" cellspacing=\"0\" style=\"width:100%\">\n\n                                    <thead>\n\n                                        <tr>\n\n                                            <th>Massa da esfera</th>\n\n                                            <th>Diametro da esfera</th>\n\n                                            <th>Percurso da esfera atrtavés do laser</th>\n\n                                            <th>Constante de elasticidade</th>\n\n                                            <th>Coeficiente de expansão termica</th>\n\n                                        </tr>\n\n                                    </thead>\n\n                                    <tbody>\n\n                                        <tr><td>2kG +/- 75g</td>\n\n                                        <td>81mm +/- 0.5mm</td>\n\n                                        <td>~81mm</td>\n\n                                        <td>200GPa</td>\n\n                                        <td>14E-6 K^-1</td>\n\n                                    </tr></tbody>\n\n\n\n\n\n\n\n                                </table>','<section class=\"intro\">\n\n                                    <p>This Experiment allows the study of the acceleration of gravity in different points of the globe. For this purpose, an observation of several pendulums placed at different latitudes and operated remotely over the internet can be used. <br> <br>However, other experimental protocols can be performed, not only in local gravity to fit a suitable geophysical model but also to study simple mechanical principles such as conservation of mechanical energy.<br><br></p>\n\n\n\n                                </section>\n\n                                <h3> Detalhes do pêndulo</h3>\n\n                                <p>Comprimento de cabo (sem contar com a esfera):<a href=\"https://groups.ist.utl.pt/wwwelab/wiki/index.php?title=P%C3%AAndulo_Mundial#Aparato_experimental\"><em>Verifique aqui para cada lugar</em></a></p>\n\n\n\n<table id=\"example_1\" class=\"ui celled padded table\" cellspacing=\"0\" style=\"width:100%\">\n\n                                    <thead>\n\n                                        <tr>\n\n                                            <th>Massa da esfera</th>\n\n                                            <th>Diametro da esfera</th>\n\n                                            <th>Percurso da esfera atrtavés do laser</th>\n\n                                            <th>Constante de elasticidade</th>\n\n                                            <th>Coeficiente de expansão termica</th>\n\n                                        </tr>\n\n                                    </thead>\n\n                                    <tbody>\n\n                                        <tr><td>2kG +/- 75g</td>\n\n                                        <td>81mm +/- 0.5mm</td>\n\n                                        <td>~81mm</td>\n\n                                        <td>200GPa</td>\n\n                                        <td>14E-6 K^-1</td>\n\n                                    </tr></tbody>\n\n\n\n\n\n\n\n                                </table>','<section class=\"intro\"><p>Esta Experiencia permite o estudo da aceleração da gravidade em diferentes pontos do globo. Para este efeito pode ser usada uma constalação de vários pêndulos colocados em diferentes latitudes e operados remotamente pela internet.<br><br>No entanto outros protocols experimentais podem ser realizados, não só na gravidade local para ajustar um modelo geofisico adequado mas também para estudar princípios mecânicos simples tais como a conservação da energia mecânica.<br><br>Latitudes de 50º a 0º no equador são acessíveis.</p></section><h3 style=\"font-family: &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; color: rgb(51, 51, 51);\">Detalhes do pêndulo</h3><p>Comprimento de cabo (sem contar com a esfera):<a href=\"https://groups.ist.utl.pt/wwwelab/wiki/index.php?title=P%C3%AAndulo_Mundial#Aparato_experimental\"><em>Verifique aqui para cada lugar</em></a></p><table id=\"example_1\" class=\"ui celled padded table\" cellspacing=\"0\" style=\"background-color: rgb(255, 255, 255); width: 681.333px;\"><thead><tr><th style=\"line-height: 1.42857;\">Massa da esfera</th><th style=\"line-height: 1.42857;\">Diametro da esfera</th><th style=\"line-height: 1.42857;\">Percurso da esfera através do laser</th><th style=\"line-height: 1.42857;\">Constante de elasticidade</th><th style=\"line-height: 1.42857;\">Coeficiente de expansão térmica</th></tr></thead><tbody><tr><td style=\"line-height: 1.42857;\">2 kg +/- 75g</td><td style=\"line-height: 1.42857;\">81mm +/- 0.5mm</td><td style=\"line-height: 1.42857;\">~81 mm</td><td style=\"line-height: 1.42857;\">200 GPa</td><td style=\"line-height: 1.42857;\">14e-6 K^-1</td></tr></tbody></table>','Physics - Mechanics','Physics - Mechanics','Física - Mecânica','Remote','Remote','Remoto','pendulum','<section class=\"intro\"><p>Esta Experiencia permite o estudo da aceleração da gravidade em diferentes pontos do globo. Para este efeito pode ser usada uma constalação de vários pêndulos colocados em diferentes latitudes e operados remotamente pela internet.<br><br>No entanto outros protocols experimentais podem ser realizados, não só na gravidade local para ajustar um modelo geofisico adequado mas também para estudar princípios mecânicos simples tais como a conservação da energia mecânica.<br><br>Latitudes de 50º a 0º no equador são acessíveis.</p></section><h3 style=\"font-family: &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; color: rgb(51, 51, 51);\">Detalhes do pêndulo</h3><p>Comprimento de cabo (sem contar com a esfera):<a href=\"https://groups.ist.utl.pt/wwwelab/wiki/index.php?title=P%C3%AAndulo_Mundial#Aparato_experimental\"><em>Verifique aqui para cada lugar</em></a></p><table id=\"example_1\" class=\"ui celled padded table\" cellspacing=\"0\" style=\"background-color: rgb(255, 255, 255); width: 681.333px;\"><thead><tr><th style=\"line-height: 1.42857;\">Massa da esfera</th><th style=\"line-height: 1.42857;\">Diametro da esfera</th><th style=\"line-height: 1.42857;\">Percurso da esfera através do laser</th><th style=\"line-height: 1.42857;\">Constante de elasticidade</th><th style=\"line-height: 1.42857;\">Coeficiente de expansão térmica</th></tr></thead><tbody><tr><td style=\"line-height: 1.42857;\">2 kg +/- 75g</td><td style=\"line-height: 1.42857;\">81mm +/- 0.5mm</td><td style=\"line-height: 1.42857;\">~81 mm</td><td style=\"line-height: 1.42857;\">200 GPa</td><td style=\"line-height: 1.42857;\">14e-6 K^-1</td></tr></tbody></table>','Remoto','Péndulo','Physics - Mechanics');
/*!40000 ALTER TABLE `free_apparatustype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_execution`
--

DROP TABLE IF EXISTS `free_execution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_execution` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`config`)),
  `status` varchar(1) NOT NULL,
  `protocol_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `apparatus_id` bigint(20) NOT NULL,
  `end` datetime(6) DEFAULT NULL,
  `start` datetime(6) DEFAULT NULL,
  `queue_time` datetime(6) DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `free_execution_protocol_id_085f9075_fk_free_protocol_id` (`protocol_id`),
  KEY `free_execution_user_id_807b47b3_fk_auth_user_id` (`user_id`),
  KEY `free_execution_apparatus_id_0085b995_fk_free_apparatus_id` (`apparatus_id`),
  CONSTRAINT `free_execution_apparatus_id_0085b995_fk_free_apparatus_id` FOREIGN KEY (`apparatus_id`) REFERENCES `free_apparatus` (`id`),
  CONSTRAINT `free_execution_protocol_id_085f9075_fk_free_protocol_id` FOREIGN KEY (`protocol_id`) REFERENCES `free_protocol` (`id`),
  CONSTRAINT `free_execution_user_id_807b47b3_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=612 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_execution`
--

LOCK TABLES `free_execution` WRITE;
/*!40000 ALTER TABLE `free_execution` DISABLE KEYS */;
/*!40000 ALTER TABLE `free_execution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_protocol`
--

DROP TABLE IF EXISTS `free_protocol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_protocol` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `name_en` varchar(64) DEFAULT NULL,
  `name_pt` varchar(64) DEFAULT NULL,
  `config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`config`)),
  `apparatus_type_id` bigint(20) NOT NULL,
  `name_es` varchar(64) DEFAULT NULL,
  `description` longtext NOT NULL,
  `description_en` longtext DEFAULT NULL,
  `description_es` longtext DEFAULT NULL,
  `description_pt` longtext DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `free_protocol_apparatus_type_id_0481d804_fk_free_appa` (`apparatus_type_id`),
  CONSTRAINT `free_protocol_apparatus_type_id_0481d804_fk_free_appa` FOREIGN KEY (`apparatus_type_id`) REFERENCES `free_apparatustype` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_protocol`
--

LOCK TABLES `free_protocol` WRITE;
/*!40000 ALTER TABLE `free_protocol` DISABLE KEYS */;
INSERT INTO `free_protocol` VALUES (1,'Pêndulo','Pendulum','Pêndulo','{\"type\": \"object\", \"properties\": {\"deltaX\": {\"type\": \"integer\", \"default\": 10, \"minimum\": 3, \"maximum\": 22, \"multipleOf\": 1}, \"samples\": {\"type\": \"integer\", \"default\": 50, \"minimum\": 4, \"maximum\": 50, \"multipleOf\": 1}}, \"required\": [\"deltaX\", \"samples\"]}',1,'Péndulo','<p>Essa é a descrição do protocolo pêndulo</p>','<p class=\"\">This text is in protocol description.</p>','','<p>Essa é a descrição do protocolo pêndulo</p>');
/*!40000 ALTER TABLE `free_protocol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_result`
--

DROP TABLE IF EXISTS `free_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_result` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `time` datetime(6) NOT NULL,
  `result_type` varchar(1) NOT NULL,
  `value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`value`)),
  `execution_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `free_result_execution_id_de1722b4` (`execution_id`),
  CONSTRAINT `free_result_execution_id_de1722b4_fk_free_execution_id` FOREIGN KEY (`execution_id`) REFERENCES `free_execution` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9134 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_result`
--

LOCK TABLES `free_result` WRITE;
/*!40000 ALTER TABLE `free_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `free_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `free_userprofile`
--

DROP TABLE IF EXISTS `free_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `free_userprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `free_userprofile_user_id_12925002_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `free_userprofile`
--

LOCK TABLES `free_userprofile` WRITE;
/*!40000 ALTER TABLE `free_userprofile` DISABLE KEYS */;
INSERT INTO `free_userprofile` VALUES (6,'a',6),(7,'s',7);
/*!40000 ALTER TABLE `free_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_association`
--

DROP TABLE IF EXISTS `social_auth_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(255) NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` varchar(255) NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `social_auth_association_server_url_handle_078befa2_uniq` (`server_url`,`handle`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_association`
--

LOCK TABLES `social_auth_association` WRITE;
/*!40000 ALTER TABLE `social_auth_association` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_code`
--

DROP TABLE IF EXISTS `social_auth_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `code` varchar(32) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `social_auth_code_email_code_801b2d02_uniq` (`email`,`code`),
  KEY `social_auth_code_code_a2393167` (`code`),
  KEY `social_auth_code_timestamp_176b341f` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_code`
--

LOCK TABLES `social_auth_code` WRITE;
/*!40000 ALTER TABLE `social_auth_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_nonce`
--

DROP TABLE IF EXISTS `social_auth_nonce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_nonce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(255) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` varchar(65) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `social_auth_nonce_server_url_timestamp_salt_f6284463_uniq` (`server_url`,`timestamp`,`salt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_nonce`
--

LOCK TABLES `social_auth_nonce` WRITE;
/*!40000 ALTER TABLE `social_auth_nonce` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_nonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_partial`
--

DROP TABLE IF EXISTS `social_auth_partial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_partial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(32) NOT NULL,
  `next_step` smallint(5) unsigned NOT NULL CHECK (`next_step` >= 0),
  `backend` varchar(32) NOT NULL,
  `data` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `social_auth_partial_token_3017fea3` (`token`),
  KEY `social_auth_partial_timestamp_50f2119f` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_partial`
--

LOCK TABLES `social_auth_partial` WRITE;
/*!40000 ALTER TABLE `social_auth_partial` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_partial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_usersocialauth`
--

DROP TABLE IF EXISTS `social_auth_usersocialauth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_usersocialauth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(32) NOT NULL,
  `uid` varchar(255) NOT NULL,
  `extra_data` longtext NOT NULL,
  `user_id` int(11) NOT NULL,
  `created` datetime(6) NOT NULL,
  `modified` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `social_auth_usersocialauth_provider_uid_e6b5e668_uniq` (`provider`,`uid`),
  KEY `social_auth_usersocialauth_user_id_17d28448_fk_auth_user_id` (`user_id`),
  KEY `social_auth_usersocialauth_uid_796e51dc` (`uid`),
  CONSTRAINT `social_auth_usersocialauth_user_id_17d28448_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_usersocialauth`
--

LOCK TABLES `social_auth_usersocialauth` WRITE;
/*!40000 ALTER TABLE `social_auth_usersocialauth` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_usersocialauth` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-05-26 16:51:20

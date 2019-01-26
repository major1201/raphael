
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

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `raphael` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `raphael`;
DROP TABLE IF EXISTS `cm_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cm_schedule` (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `type` int(11) DEFAULT NULL,
  `data` text COLLATE utf8mb4_unicode_ci,
  `starttime` datetime DEFAULT NULL,
  `endtime` datetime DEFAULT NULL,
  `func` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `args` text COLLATE utf8mb4_unicode_ci,
  `maxinstance` int(11) DEFAULT NULL,
  `module` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sourceid` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enabled` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `cm_schedule` WRITE;
/*!40000 ALTER TABLE `cm_schedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `cm_schedule` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `cm_schedule_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cm_schedule_log` (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `scheduleid` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `executiontime` datetime DEFAULT NULL,
  `retval` text COLLATE utf8mb4_unicode_ci,
  `status` int(11) DEFAULT NULL,
  `exception` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `cm_schedule_log` WRITE;
/*!40000 ALTER TABLE `cm_schedule_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `cm_schedule_log` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `cm_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cm_setting` (
  `id` varchar(32) NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `cm_setting` WRITE;
/*!40000 ALTER TABLE `cm_setting` DISABLE KEYS */;
INSERT INTO `cm_setting` VALUES ('0114c1afbc214edb821379fe7b5b419d','2017-05-18 08:56:25','2017-05-18 12:59:21','system.otp.enabled','no'),('0e029e1ab22e4a5aa1788f82ddf9d25e','2018-09-07 06:23:46','2018-09-07 06:23:46','openldap.ou_host_groups','hostGroups'),('116b1aaae89b48aab20bfba917242d58','2018-08-15 08:43:38','2018-08-15 08:43:38','openldap.ou_groups','groups'),('12eaa90abb4a4ff6bdaf9562417c1cf8','2017-05-17 09:02:02','2017-05-17 09:23:32','system.display.title','Raphael'),('1d418affa6194edcabdae8a4e0d5afef','2018-08-16 02:41:10','2018-08-16 02:41:10','openldap.shadow.warning','10'),('29124e1d058844f9892f9697a227ee8f','2018-08-15 08:41:19','2018-08-15 08:41:32','openldap.manager','cn=ldapadm,dc=example,dc=com'),('37a879dbf0994d27a63786541040cb3a','2018-08-15 08:42:32','2018-08-15 08:42:32','openldap.passwd','password'),('457d4d02784f40378941c086dc1b5e66','2017-05-18 12:19:28','2017-05-18 12:19:28','system.tempdir','/tmp'),('45ef826c06164127a5857130de07a772','2018-08-16 02:37:49','2018-09-07 09:43:14','openldap.shadow.min','0'),('4983fc7538954195bfb4eb26bb872e22','2017-05-17 09:25:15','2018-08-15 03:17:18','system.display.footer','©Example <a class=\"footer-beian\" target=\"_blank\" href=\"http://www.example.com/\">Example.com</a>'),('49d36b6a45ae4c909861f4dd120fdfa1','2018-09-18 11:07:59','2018-09-18 11:07:59','system.session.timeout','86400'),('4d00bec6333b4b3a90dd3c06eef50663','2018-09-07 06:23:37','2018-09-07 06:23:37','openldap.ou_hosts','hosts'),('4dd4461905a6456ab0bab4cf6b7063a6','2018-08-15 03:31:47','2018-09-07 09:14:57','openldap.uri','ldap://192.168.1.101'),('5f91b6e21bc7421180689fb974be087f','2018-08-15 08:40:04','2018-08-15 08:40:04','openldap.basedn','dc=example,dc=com'),('a6141477a0924a3787a369bef2f7da2e','2018-09-07 06:24:12','2018-09-07 06:24:12','openldap.ou_services','services'),('a95b35febcd5412680962e9570b29bab','2018-09-07 06:24:03','2018-09-07 06:24:03','openldap.ou_command_groups','commandGroups'),('b9bcea8403c94c16ac4306c2e8b82b14','2018-09-07 06:23:56','2018-09-07 06:23:56','openldap.ou_commands','commands'),('cdc6240b83cc4589b997c1bd78021eb4','2018-08-15 08:43:29','2018-08-15 08:43:29','openldap.ou_people','people'),('d3142fa360c44df8952043d7f0177d03','2018-08-16 02:41:57','2018-08-16 02:41:57','openldap.shadow.inactive','3'),('e5d0ccc1d25f4f00bf007dc123548767','2018-08-16 02:38:14','2018-08-16 02:38:14','openldap.shadow.max','90'),('9e3004671b1f4bfdbf10a1b85424d5ca','2018-12-28 10:38:47','2018-12-28 10:39:23','openldap.start_tls','false');
/*!40000 ALTER TABLE `cm_setting` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `value` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userid` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uri` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_auth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_auth` (
  `id` varchar(32) NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `sourceid` varchar(300) DEFAULT NULL,
  `sourceentity` varchar(300) DEFAULT NULL,
  `grantid` varchar(300) DEFAULT NULL,
  `grantentity` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_auth` WRITE;
/*!40000 ALTER TABLE `um_auth` DISABLE KEYS */;
/*!40000 ALTER TABLE `um_auth` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_function`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_function` (
  `id` varchar(32) NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `name` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_function` WRITE;
/*!40000 ALTER TABLE `um_function` DISABLE KEYS */;
INSERT INTO `um_function` VALUES ('9cb80f7c378c11e588da00163e003ac0','0000-00-00 00:00:00','0000-00-00 00:00:00','SYSTEM');
/*!40000 ALTER TABLE `um_function` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_login_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_login_source` (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `type` int(11) DEFAULT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uri` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `filter` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_login_source` WRITE;
/*!40000 ALTER TABLE `um_login_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `um_login_source` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_menu` (
  `id` varchar(32) NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `target` varchar(100) DEFAULT NULL,
  `sort` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `parentid` varchar(32) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `mark` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_menu` WRITE;
/*!40000 ALTER TABLE `um_menu` DISABLE KEYS */;
INSERT INTO `um_menu` VALUES ('064d3336fa0849de906814cfcbff0f3d','2018-08-15 06:10:58','2018-08-15 06:32:45','主机管理','/openldap/hosts','_self',2,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-server','openldap_hosts'),('15161a5715d946e2a50df200cde58472','2018-08-15 06:09:17','2018-08-15 06:09:17','用户管理','/openldap/users','_self',1,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-user','openldap_users'),('2af022cd2d674a04ab2c181bba4db399','2018-08-15 03:29:50','2018-08-15 03:29:56','OpenLDAP',NULL,'_self',1,1,'','fa fa-users',''),('2b554c68278f4c5591360dc6fb5dfbfc','0000-00-00 00:00:00','2018-08-15 05:22:34','定时任务','/schedule','_self',5,0,'9ea069ff48754cdaadb9b4ef9a654fb9','fa fa-clock-o','scheduler'),('33d65a6056054aa6aa1dd772c9f6e32d','2018-08-15 06:16:30','2018-08-15 06:32:16','服务管理','/openldap/services','_self',4,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-male','openldap_services'),('507bef4ee8f24ace81e784288fddfe2b','2017-05-17 05:02:09','2018-08-15 05:22:24','设置管理','/setting','_self',4,0,'9ea069ff48754cdaadb9b4ef9a654fb9','fa fa-cog','cm.setting'),('687007e77f9a4b5198198d38fc485bd2','0000-00-00 00:00:00','2018-08-15 05:22:13','功能管理','/function','_self',3,0,'9ea069ff48754cdaadb9b4ef9a654fb9','fa fa-th','function'),('6c8ef60aaa5d4b87988f6fbfcded4539','2018-08-15 06:12:47','2018-08-31 03:30:32','命令管理','/openldap/commands','_self',3,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-terminal','openldap_commands'),('9ea069ff48754cdaadb9b4ef9a654fb9','2017-04-08 06:42:46','2018-08-15 05:21:44','系统管理',NULL,'_self',2,1,'','fa fa-cog',''),('ae4e03aa12fb43a8b7aaeebce628520a','2018-08-15 06:17:25','2018-09-07 05:14:25','设置','/openldap/setting','_self',6,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-gear','openldap_setting'),('c463ef019b424134a6e39500b42ba807','0000-00-00 00:00:00','2018-08-15 05:22:05','菜单管理','/menu','_self',2,0,'9ea069ff48754cdaadb9b4ef9a654fb9','fa fa-list-alt','menu'),('d14c82ced0424cd88822ecdbf9b95095','2018-08-23 10:46:20','2018-08-23 10:46:25','授权关系管理','/openldap/auth','_self',5,0,'2af022cd2d674a04ab2c181bba4db399','fa fa-users','openldap_auth'),('f40bc3cc06d84ba59bf503769659b769','0000-00-00 00:00:00','2018-08-15 05:21:58','用户管理','/user','_self',1,0,'9ea069ff48754cdaadb9b4ef9a654fb9','fa fa-users','user');
/*!40000 ALTER TABLE `um_menu` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_session` (
  `id` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `token` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `expire_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_session` WRITE;
/*!40000 ALTER TABLE `um_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `um_session` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `um_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `um_user` (
  `id` varchar(32) NOT NULL,
  `utc_create` datetime NOT NULL,
  `utc_modified` datetime NOT NULL,
  `loginid` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `salt` varchar(32) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `otpsecret` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `um_user` WRITE;
/*!40000 ALTER TABLE `um_user` DISABLE KEYS */;
INSERT INTO `um_user` VALUES ('022e8edc263911e588da00163e003ac0','0000-00-00 00:00:00','0000-00-00 00:00:00','guest','Guest',NULL,NULL,NULL,NULL),('f0812d5a263811e588da00163e003ac0','0000-00-00 00:00:00','2017-04-29 06:08:11','admin','Admin','339432d5442c5781e3bcfc6c59273e7e2ec418cd36e676ad74666709b73a6311d50e47ea759c612ff2804da64030d8f946e1b9af9dd436355cc9fd23d62895b6','01cba6fd8a3c4475bd463754a3eed1f7',NULL,NULL);
/*!40000 ALTER TABLE `um_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


CREATE TABLE `hosts_ipv4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_ip` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `host_ports_ipv4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_id` int(8) NOT NULL REFERENCES hosts_ipv4(id),
  `port` int(8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `scan_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scantime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `host_id` int(8) NOT NULL REFERENCES hosts_ipv4(id),
  `port` int(8) NOT NULL,
  `status` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
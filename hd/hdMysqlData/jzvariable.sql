-- create database if not exists `hd`;
use `hd`;

-- create table if not exists `jzvariable` ( 
-- 	`jid` int unsigned NOT NULL auto_increment, 
-- 	`parentid` int not null, 
-- 	`jzname` varchar(100) not null,
--     `aliasname` varchar(100),
-- 	primary key(`jid`),
--     UNIQUE KEY `jzname` (`jzname`)
-- )default charset=utf8;
delete from jzvariable;

insert into jzvariable (jid,parentid,jzname,aliasname) values 
	(1,0,'23号机组','23'),
	(2,0,'24号机组','24'),
	(3,0,'25号机组','25'),
	(4,0,'26号机组','26');

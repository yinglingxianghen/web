-- Author: An Yang
-- Create time: 2017-07-19

-- create database if not exists `hd`;
use `hd`;

-- create table if not exists `threshold` ( 
-- 	`id` int unsigned auto_increment, 
-- 	`name` varchar(100) not null, 
-- 	`GBL` int not null default 0,
-- 	`GBH` int not null default 0,
-- 	`HECL` int not null default 0,
-- 	`HECH` int not null default 0,
-- 	`contractL` int not null default 0,
-- 	`contractH` int not null default 0,
-- 	primary key(`id`) 
-- )default charset=utf8;

delete from threshold;

insert into threshold (name,GBL,GBH,HECL,HECH,contractL,contractH,aliasname) values
	('转轮上腔压力脉动峰峰值',0,0,0,6,0,8,''),
	('无叶区压力脉动峰峰值',0,0,0,6,0,8,'ylmdwy'),
	('蜗壳进口压力脉动峰峰值',0,0,0,6,0,8,'ylmdwk'),
	('尾水管上游侧压力脉动峰峰值',0,0,0,6,0,8,'ylmdshang'),
	('尾水管下游侧压力脉动峰峰值',0,0,0,6,0,8,'ylmdxia'),
	('水导轴承X方向摆度峰峰值',0,270,0,280,0,200,'shuix'),
	('水导轴承Y方向摆度峰峰值',0,225,0,280,0,200,'shuiy'),
	('顶盖X方向水平振动峰峰值',0,90,0,90,0,80,'dinggx'),
	('顶盖Y方向水平振动峰峰值',0,90,0,90,0,80,'dinggy'),
	('顶盖X方向垂直振动峰峰值',0,90,0,110,0,90,'dinggz'),
	('下机架X方向水平振动峰峰值',0,110,0,40,0,0,'xiajjx'),
	('下机架Y方向水平振动峰峰值',0,110,0,40,0,0,'xiajjy'),
	('下机架X方向垂直振动峰峰值',0,80,0,40,0,30,'xiajjz'),
	('下导轴承X方向摆度峰峰值',0,510,0,300,0,0,'xiax'),
	('下导轴承Y方向摆度峰峰值',0,510,0,300,0,0,'xiay'),
	('上机架X方向水平振动峰峰值',0,110,0,80,0,80,'shangjjx'),
	('上机架Y方向水平振动峰峰值',0,110,0,80,0,80,'shangjjy'),
	('上机架X方向垂直振动峰峰值',0,0,0,80,0,0,'shangjjz'),
	('上导轴承X方向摆度峰峰值',0,225,0,300,0,0,'shangx'),
	('上导轴承Y方向摆度峰峰值',0,225,0,300,0,0,'shangy'),
	('定子机架X方向水平振动峰峰值',0,40,0,30,0,20,'dingjjx'),
	('定子机架Y方向水平振动峰峰值',0,40,0,30,0,20,'dingjjy'),
	('定子机架X方向垂直振动峰峰值',0,0,0,30,0,0,'dingjjz');


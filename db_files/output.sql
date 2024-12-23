PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users ( id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, rfid_tag TEXT NOT NULL UNIQUE, light_threshold INTEGER NOT NULL, temp_threshold INTEGER NOT NULL);
INSERT INTO users VALUES(1,'Bratushka Denis','2249436@edu.vaniercollege.qc.ca','532e97a6',400,21);
INSERT INTO users VALUES(2,'Zlatin','zlatintsvetkov@gmail.com','83560396',600,25);
CREATE TABLE activity_logs ( id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, action TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id));
INSERT INTO activity_logs VALUES(1,1,'login','2024-11-21 06:08:52');
INSERT INTO activity_logs VALUES(2,1,'login','2024-11-21 06:25:04');
INSERT INTO activity_logs VALUES(3,1,'login','2024-11-21 06:39:36');
INSERT INTO activity_logs VALUES(4,2,'login','2024-11-21 01:42:30.456773');
INSERT INTO activity_logs VALUES(5,2,'login','2024-11-21 02:30:12.360480');
INSERT INTO activity_logs VALUES(6,2,'login','2024-11-21 02:30:25.986941');
INSERT INTO activity_logs VALUES(7,1,'login','2024-11-21 07:30:34');
INSERT INTO activity_logs VALUES(8,1,'login','2024-11-21 07:30:36');
INSERT INTO activity_logs VALUES(9,1,'login','2024-11-21 07:30:37');
INSERT INTO activity_logs VALUES(10,1,'login','2024-11-21 07:30:37');
INSERT INTO activity_logs VALUES(11,1,'login','2024-11-21 07:30:37');
INSERT INTO activity_logs VALUES(12,1,'login','2024-11-21 07:30:38');
INSERT INTO activity_logs VALUES(13,2,'login','2024-11-22 03:26:17');
INSERT INTO activity_logs VALUES(14,2,'login','2024-11-22 03:26:18');
INSERT INTO activity_logs VALUES(15,2,'login','2024-11-22 03:26:24');
INSERT INTO activity_logs VALUES(16,2,'login','2024-11-22 03:31:33');
INSERT INTO activity_logs VALUES(17,2,'login','2024-11-22 03:31:41');
INSERT INTO activity_logs VALUES(18,2,'login','2024-11-22 03:31:43');
INSERT INTO activity_logs VALUES(19,2,'login','2024-11-22 03:48:38');
INSERT INTO activity_logs VALUES(20,2,'login','2024-11-22 03:48:40');
INSERT INTO activity_logs VALUES(21,2,'login','2024-11-22 03:49:08');
INSERT INTO activity_logs VALUES(22,1,'login','2024-11-22 03:49:30');
INSERT INTO activity_logs VALUES(23,2,'login','2024-11-22 03:50:59');
INSERT INTO activity_logs VALUES(24,2,'login','2024-11-22 03:51:00');
INSERT INTO activity_logs VALUES(25,2,'login','2024-11-22 03:51:06');
INSERT INTO activity_logs VALUES(26,2,'login','2024-11-22 03:51:13');
INSERT INTO activity_logs VALUES(27,2,'login','2024-11-22 03:51:14');
INSERT INTO activity_logs VALUES(28,2,'login','2024-11-22 03:52:19');
INSERT INTO activity_logs VALUES(29,2,'login','2024-11-22 03:52:21');
INSERT INTO activity_logs VALUES(30,2,'login','2024-11-22 23:37:21');
INSERT INTO activity_logs VALUES(31,2,'login','2024-11-22 23:37:23');
INSERT INTO activity_logs VALUES(32,2,'login','2024-11-22 23:39:02');
INSERT INTO activity_logs VALUES(33,2,'login','2024-11-22 23:39:04');
INSERT INTO activity_logs VALUES(34,2,'login','2024-11-22 23:39:05');
INSERT INTO activity_logs VALUES(35,2,'login','2024-11-22 23:39:06');
INSERT INTO activity_logs VALUES(36,2,'login','2024-11-22 23:39:41');
INSERT INTO activity_logs VALUES(37,2,'login','2024-11-23 01:07:43');
INSERT INTO activity_logs VALUES(38,2,'login','2024-11-23 01:07:45');
INSERT INTO activity_logs VALUES(39,2,'login','2024-11-23 01:07:54');
INSERT INTO activity_logs VALUES(40,2,'login','2024-11-23 01:09:58');
INSERT INTO activity_logs VALUES(41,2,'login','2024-11-23 01:38:03');
INSERT INTO activity_logs VALUES(42,2,'login','2024-11-23 02:35:23');
INSERT INTO activity_logs VALUES(43,2,'login','2024-11-23 02:35:28');
INSERT INTO activity_logs VALUES(44,2,'logout','2024-11-23 02:38:08');
INSERT INTO activity_logs VALUES(45,2,'login','2024-11-23 02:38:14');
INSERT INTO activity_logs VALUES(46,1,'login','2024-11-23 02:38:19');
INSERT INTO activity_logs VALUES(47,1,'logout','2024-11-23 02:40:25');
INSERT INTO activity_logs VALUES(48,1,'login','2024-11-23 02:48:37');
INSERT INTO activity_logs VALUES(49,1,'logout','2024-11-23 02:49:02');
INSERT INTO activity_logs VALUES(50,2,'login','2024-11-23 02:49:13');
INSERT INTO activity_logs VALUES(51,2,'logout','2024-11-23 02:49:21');
INSERT INTO activity_logs VALUES(52,1,'login','2024-11-25 16:25:43');
INSERT INTO activity_logs VALUES(53,1,'logout','2024-11-25 16:27:19');
INSERT INTO activity_logs VALUES(54,1,'login','2024-11-25 16:27:24');
INSERT INTO activity_logs VALUES(55,1,'logout','2024-11-25 16:29:03');
INSERT INTO activity_logs VALUES(56,2,'login','2024-11-25 16:29:08');
INSERT INTO activity_logs VALUES(57,2,'logout','2024-11-25 16:29:19');
INSERT INTO activity_logs VALUES(58,2,'login','2024-11-25 16:29:25');
INSERT INTO activity_logs VALUES(59,2,'logout','2024-11-25 16:29:39');
INSERT INTO activity_logs VALUES(60,2,'login','2024-11-25 16:29:45');
INSERT INTO activity_logs VALUES(61,2,'logout','2024-11-25 16:29:50');
INSERT INTO activity_logs VALUES(62,2,'login','2024-11-25 16:29:55');
INSERT INTO activity_logs VALUES(63,1,'login','2024-11-25 16:35:20');
INSERT INTO activity_logs VALUES(64,1,'logout','2024-11-25 16:35:30');
INSERT INTO activity_logs VALUES(65,2,'login','2024-11-25 16:35:45');
INSERT INTO activity_logs VALUES(66,2,'logout','2024-11-25 16:37:36');
INSERT INTO activity_logs VALUES(67,2,'login','2024-11-25 16:37:51');
INSERT INTO activity_logs VALUES(68,2,'logout','2024-11-25 16:38:01');
INSERT INTO activity_logs VALUES(69,1,'login','2024-11-25 16:38:16');
INSERT INTO activity_logs VALUES(70,1,'logout','2024-11-25 16:58:20');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',2);
INSERT INTO sqlite_sequence VALUES('activity_logs',70);
COMMIT;

CREATE TABLE IF NOT EXISTS `devices` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `ip_address` VARCHAR(15) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `last_seen` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE `devices`
  CHANGE `last_seen` `last_seen` TIMESTAMP NOT NULL DEFAULT (UTC_TIMESTAMP());

CREATE TABLE IF NOT EXISTS `device_commands` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `device_id` BIGINT UNSIGNED NOT NULL,
    `command` VARCHAR(32) NOT NULL,
    `parameters` JSON,
    `time_submitted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    constraint fk_device_id foreign key (device_id) references devices(id) ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE `device_commands`
  CHANGE `time_submitted` `time_submitted` TIMESTAMP NOT NULL DEFAULT (UTC_TIMESTAMP());
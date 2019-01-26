CREATE TABLE um_login_source (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  type         INTEGER, -- 0: local, 1: ldap
  name         VARCHAR(255),
  uri          VARCHAR(255),
  filter       TEXT
);

CREATE TABLE um_user (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  login_source VARCHAR(32), -- um_login_source.id
  loginid      VARCHAR(255),
  name         VARCHAR(255),
  password     VARCHAR(128), -- sha512(salt + password)
  salt         VARCHAR(32), -- the salt for hashing password
  email        VARCHAR(255),
  otpsecret    VARCHAR(16),
  is_admin     INTEGER
);

CREATE TABLE um_session (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  token        VARCHAR(32),
  user_id      VARCHAR(32),
  expire_at    DATETIME -- utc time
);

CREATE TABLE um_menu (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  name         VARCHAR(255),
  url          VARCHAR(255),
  target       VARCHAR(100),
  sort         INTEGER,
  type         INTEGER, -- 0: menu item, 1: directory
  parentid     VARCHAR(32),
  icon         VARCHAR(255),
  mark         VARCHAR(100)
);

CREATE TABLE um_function (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  name         VARCHAR(300)
);

CREATE TABLE um_auth (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  sourceid     VARCHAR(300),
  sourceentity VARCHAR(300),
  grantid      VARCHAR(300),
  grantentity  VARCHAR(300)
);

CREATE TABLE cm_setting (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  name         VARCHAR(255),
  value        VARCHAR(255)
);

CREATE TABLE cm_schedule (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  type         INTEGER, -- 1: date, 2: inteval, 3: cron
  data         TEXT, -- detail data
  starttime    DATETIME,
  endtime      DATETIME,
  func         VARCHAR(255), -- invoke function
  args         TEXT, -- args and kwargs in json {"args": [xxx, xxx], "kwargs": {xxx: xxx, xxx: xxx}}
  maxinstance  INTEGER, -- max concurrent instance
  module       VARCHAR(255), -- identify the source
  sourceid     VARCHAR(32),
  enabled      INTEGER -- 0: disabled, 1: enabled
);

CREATE TABLE cm_schedule_log (
  id            VARCHAR(32) PRIMARY KEY,
  utc_create    DATETIME NOT NULL,
  utc_modified  DATETIME NOT NULL,
  scheduleid    VARCHAR(32),
  executiontime DATETIME,
  retval        TEXT,
  status        INTEGER, -- 1: executed, 2: error, 3: missed, 4: hit_max_instance
  exception     VARCHAR(255)
);

CREATE TABLE log (
  id           VARCHAR(32) PRIMARY KEY,
  utc_create   DATETIME NOT NULL,
  utc_modified DATETIME NOT NULL,
  category     VARCHAR(100),
  name         VARCHAR(100),
  value        VARCHAR(100),
  userid       VARCHAR(32),
  ip           VARCHAR(255),
  uri          TEXT(3000) -- URI&parameters
);

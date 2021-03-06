#ifndef DATATYPES_H
#define DATATYPES_H
// datatypes and defines

// whenever creating connection name, it's CONNECTION_PREFIX + connection id
#define CONNECTION_PREFIX "conn"

#define LINKHIVE_NAME "Linkhive"
#define LINKHIVE_VERSION "0.1"

// for QSettings
#define SETTINGS_TABLE_GROUP "tables"
#define SETTINGS_CONFIG_GROUP "configs"
#define SETTINGS_CONFIG_HOST "host"
#define SETTINGS_CONFIG_USER "user"
#define SETTINGS_CONFIG_PASS "pass"
#define SETTINGS_CONFIG_DB "db"
#define SETTINGS_CONFIG_TYPE "type"

#define URL_REGEXP "^https?://([-\\w\\.]+)+(:\\d+)?(/([\\w/_\\.]*(\\?\\S+)?)?)?"

#endif

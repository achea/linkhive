#include "lhglobals.h"
#include "datatypes.h"

#include <QString>
#include <QStringList>
//#include <QMessageBox>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>

//#include <QtGlobal>
#include <QSettings>

bool LhGlobals::readSettings()
{
	QSettings settings(QSettings::IniFormat, QSettings::UserScope, LINKHIVE_NAME,"");

	tableNames.clear();
	settings.beginGroup(SETTINGS_TABLE_GROUP);		
	QString name;
	int id;
	foreach(name, settings.childKeys())		// childKeys() returns QStringList
	{
		// get the connection id associated with the table name
		id = settings.value(name).toInt();		// QVariant to int
		tableNames.insert(name,id);
	}
	settings.endGroup();

	connectionConfigs.clear();
	settings.beginGroup(SETTINGS_CONFIG_GROUP);
	QString idStr;
	bool status;
	// TODO typedef
	QHash<QString, QString> tempConfig;
	QHash<QString, QVariant> temp1;
	foreach(idStr, settings.childKeys())
	{
		// saved as QHash<QString, QVariant>
		//    where QVariant is saved as QHash<QString, QVariant>
		// want as QHash<int, QHash<QString, QString> >
		temp1 = settings.value(idStr).toHash();		// now have inside QHash

		tempConfig.clear();
		foreach(name, temp1.keys())
		{
			tempConfig.insert(name, temp1.value(name).toString());
		}
		connectionConfigs.insert(idStr.toInt(&status),tempConfig);
		Q_ASSERT(status);
	}

	// TODO error checking
	return true;
}

bool LhGlobals::createConnections()
{
	bool status = true;		// default true
	QSqlDatabase db;
	QString connName;
	QHash<QString,QString> temp;

	int key;
	foreach (key, this->connectionConfigs.keys())
	{
		connName = "conn";
		connName.append(QString::number(key));
		temp = this->connectionConfigs.value(key);

		db = QSqlDatabase::addDatabase("QMYSQL",connName);
			// if connName is already opened, Qt will close it for us before opening it again
		//db.setDatabaseName(":memory:");
		db.setHostName(temp.value("host"));
		db.setDatabaseName(temp.value("db"));
		db.setUserName(temp.value("user"));
		db.setPassword(temp.value("pass"));
		if (!db.open())
		{
			status = false;
		}
		else { connectionNames.insert(key,connName);
		}
		// what to do with db now?
	}

	return status;
}

bool LhGlobals::closeAllDbs()
{
	bool status = true;
	QList<int> closed;

	// get the keys from connectionNames
	QHash<int, QString>::const_iterator i = connectionNames.constBegin();
	while (i != connectionNames.constEnd())
	{
		// removeDatabase() needs connection name
		// not allowed any open queries, or warning will appear .. somewhere
		QSqlDatabase::removeDatabase(i.value());		// void, so no status returned
														// but can check if contained in list
		if (QSqlDatabase::contains(i.value()))		// not yet removed
		{
			status = false;
		} else
		{
			// can remove while still iterating??  Assume no...
			closed.append(i.key());
		}

		++i;
	}

	// remove from QHash after iterating
	// remove from last to first, because removeAt() will then mess with the ordering at each removeAt()
	//    so sort descending (it is a QList, so has order)
	qSort(closed.begin(),closed.end(),qGreater<int>() );
	int key;
	foreach (key, closed)
	{
		connectionNames.remove(key);
	}

	return status;
}

QString LhGlobals::getConnNameFromTableName(QString tableName)
{
	// as the function says
	// map from tablename to id to conn name
	if (!tableNames.contains(tableName)) 
	{
		return "";
	} else
	{
		return connectionNames.value(tableNames.value(tableName));
	}
}

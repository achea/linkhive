#include "lhglobals.h"

#include <QString>
//#include <QMessageBox>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>

bool LhGlobals::readSettings()
{
	tableNames.insert("reddit_stories",0);
	tableNames.insert("hn_stories",0);

	QHash<QString,QString> temp;
	temp.insert("host","localhost");
	temp.insert("user","achea");
	temp.insert("pass","asdf");
	temp.insert("db","linkhive");
	connectionConfigs.insert(0,temp);

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

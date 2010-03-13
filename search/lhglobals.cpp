#include "lhglobals.h"
#include "datatypes.h"

#include <algorithm>

#include <QString>
#include <QStringList>
//#include <QMessageBox>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>

#include <QtDebug>
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

bool LhGlobals::readSettings2()
{
	// read settings that are human-readable/writable
	// saved indexes starts from 1 instead of 0
	QSettings settings(QSettings::IniFormat, QSettings::UserScope, LINKHIVE_NAME,"");

	QStringList strList = settings.childGroups();
	if (!(strList.contains(SETTINGS_TABLE_GROUP) and strList.contains(SETTINGS_CONFIG_GROUP)))
		return false;
	tableNames.clear();
	settings.beginGroup(SETTINGS_TABLE_GROUP);
	QString name;
	QVariant temp;
	bool status;
	int id;
	foreach(name, settings.childKeys())
	{
		temp = settings.value(name);	// temp is a QVariant(QString)
		//if (temp.type() != QVariant::Int)	// must be an int
		//	return false;
		// convert to int
		id = temp.toInt(&status);
		Q_ASSERT(status);
		tableNames.insert(name,id);
	}
	settings.endGroup();

	// we have already checked that SETTINGS_CONFIG_GROUP exists
	connectionConfigs.clear();
	/*settings.beginGroup(SETTINGS_CONFIG_GROUP);
	QString idStr;

	foreach(idStr, settings.childKeys())
	{
		// each id must have 

	}*/

	QHash<QString, QString> tempConfig;
	int size = settings.beginReadArray(SETTINGS_CONFIG_GROUP);
	for (id = 0; id < size; ++id)
	{
		// if one of these aren't here, createConnections will be the one to fail
		settings.setArrayIndex(id);
		tempConfig.clear();
		tempConfig.insert(SETTINGS_CONFIG_HOST, settings.value(SETTINGS_CONFIG_HOST).toString());
		tempConfig.insert(SETTINGS_CONFIG_USER, settings.value(SETTINGS_CONFIG_USER).toString());
		tempConfig.insert(SETTINGS_CONFIG_PASS, settings.value(SETTINGS_CONFIG_PASS).toString());
		tempConfig.insert(SETTINGS_CONFIG_DB, settings.value(SETTINGS_CONFIG_DB).toString());
		tempConfig.insert(SETTINGS_CONFIG_TYPE, settings.value(SETTINGS_CONFIG_TYPE).toString());
		connectionConfigs.insert(id, tempConfig);
	}
	settings.endArray();
	//qDebug() << connectionConfigs;

	// TODO error checking
	return true;
}

bool LhGlobals::saveSettings()
{
	// TODO maybe private QSettings rather than two local ones?
	QSettings settings(QSettings::IniFormat, QSettings::UserScope, LINKHIVE_NAME,"");

	settings.beginGroup(SETTINGS_TABLE_GROUP);
	QString name;
	foreach(name, tableNames.keys())
	{
		settings.setValue(name,tableNames.value(name));
	}
	settings.endGroup();

	settings.beginGroup(SETTINGS_CONFIG_GROUP);
	int id;
	QString idStr;
	QHash<QString, QVariant> tempConfig;
	foreach(id, connectionConfigs.keys())
	{
		tempConfig.clear();
		foreach (idStr, connectionConfigs.value(id).keys())
		{
			tempConfig.insert(idStr, QVariant(connectionConfigs.value(id).value(idStr)));
		}

		settings.setValue(QString::number(id),QVariant(tempConfig));
	}
	settings.endGroup();
	
	return true;
}

bool LhGlobals::saveSettings2()
{
	// human-readable save-settings
	this->sequentialize();
	
	QSettings settings(QSettings::IniFormat, QSettings::UserScope, LINKHIVE_NAME,"");

	settings.beginGroup(SETTINGS_TABLE_GROUP);
	settings.remove("");		// remove all items in current group
	QString name;
	foreach(name, tableNames.keys())
	{
		settings.setValue(name,tableNames.value(name));
	}
	settings.endGroup();

	settings.beginWriteArray(SETTINGS_CONFIG_GROUP);
	settings.remove("");		// remove all items in current group (opened with beginWriteArray instead of beginGroup, but still works)
	for (int id = 0; id < connectionConfigs.size(); ++id)		
	{
		settings.setArrayIndex(id);			// id = 0 is config 1
		settings.setValue(SETTINGS_CONFIG_HOST, connectionConfigs.value(id).value(SETTINGS_CONFIG_HOST));
		settings.setValue(SETTINGS_CONFIG_USER, connectionConfigs.value(id).value(SETTINGS_CONFIG_USER));
		settings.setValue(SETTINGS_CONFIG_PASS, connectionConfigs.value(id).value(SETTINGS_CONFIG_PASS));
		settings.setValue(SETTINGS_CONFIG_DB, connectionConfigs.value(id).value(SETTINGS_CONFIG_DB));
		settings.setValue(SETTINGS_CONFIG_TYPE, connectionConfigs.value(id).value(SETTINGS_CONFIG_TYPE));
	}
	settings.endArray();

	return true;
}

bool LhGlobals::sequentialize()
{
	// in preparation for beginWriteArray
	// each table config must start from 0 and sequence 1 by 1 to it's length
	//   if it is missing, then change that value and copy the 
	
	// TODO typedef
	QHash<QString,int> tempTableNames;
	QHash<int,QHash<QString,QString> > tempConnectionConfigs;
	tempTableNames.clear();
	tempConnectionConfigs.clear();

	QList<int> id_list = tableNames.values();		// get the values
	qSort(id_list.begin(),id_list.end());			// sort ascending

	int size1 = id_list.size();
	int size = std::max(size1+1, id_list.last()+1);			// sorted, so last item is the largest
												// add one for off-by-1 discrepancy
	int* id_count = new int[size];				// for frequency count

	int x;
	for (x = 0; x < size; x++)
		id_count[x] = 0;
	foreach(x, id_list)				// actual frequency count
	{
		id_count[x] = id_count[x]+1;
	}

	QString name;
	int unique_count = 0;				
	for (x = 0; x < size; x++)
	{
		if (id_count[x] > 0)			//if there is one
		{
			// for each key in tableNames with value x
			//    add to a temp QHash with value unique_count
			
			QHash<QString, int>::const_iterator i = tableNames.constBegin();
			while (i != tableNames.constEnd()) 
			{
				//cout << i.key() << ": " << i.value() << endl;
				if (i.value() == x)
				{
					tempTableNames.insert(i.key(),unique_count);		// +1
				}
				++i;
			}

			// now the connectionConfigs
			QHash<int,QHash<QString,QString> >::const_iterator j = connectionConfigs.constBegin();
			while (j != connectionConfigs.constEnd())
			{
				if (j.key() == x)
				{
					tempConnectionConfigs.insert(unique_count, connectionConfigs.value(j.key()));
				}
				j++;
			}
			unique_count++;
		}
	}
	//qDebug() << tableNames << endl << tempTableNames << endl << connectionConfigs << endl << tempConnectionConfigs;
	tableNames = tempTableNames;
	connectionConfigs = tempConnectionConfigs;

	// FIXME connNames might be invalid
	//   can close all and reopen all
	//   or close and reopen only those that changed
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

#ifndef CONNECTION_H
#define CONNECTION_H

#include <QMessageBox>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>

/*
    This file defines a helper function to open a connection to an
    in-memory SQLITE database and to create a test table.

    If you want to use another database, simply modify the code
    below. All the examples in this directory use this function to
    connect to a database.
*/
//! [0]
static bool createConnection()
{
	// how to close db?
    QSqlDatabase db = QSqlDatabase::addDatabase("QMYSQL");
	//db.setDatabaseName(":memory:");
	db.setHostName("localhost");
	db.setDatabaseName("linkhive");
	db.setUserName("achea");
	db.setPassword("asdf");
    if (!db.open()) {
        QMessageBox::critical(0, qApp->tr("Cannot open database"),
            qApp->tr("Unable to establish a database connection.\n"
                     "This example needs MySQL support. Please read "
                     "the Qt SQL driver documentation for information how "
                     "to build it.\n\n"
                     "Click Cancel to exit."), QMessageBox::Cancel);
        return false;
    }

//    QSqlQuery query;



    return true;
}
//! [0]

#endif

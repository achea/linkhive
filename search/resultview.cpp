#include "resultview.h"
#include "lhglobals.h"

#include <QTableView>
#include <QSqlQueryModel>
#include <QtGlobal>

ResultView::ResultView(QWidget *parent) : QTabWidget(parent)
{
	// add a new tab with QTableView with nothing
	QSqlQueryModel *model = new QSqlQueryModel;
	// the text for the query defaults to boring count 
	model->setQuery("SELECT COUNT(*) FROM reddit_stories", QSqlDatabase::database(LhGlobals::Instance().getConnNameFromTableName("reddit_stories")));
	QTableView *tableView = new QTableView;
	tableView->setModel(model);
	tableView->setEditTriggers(QAbstractItemView::NoEditTriggers);

	addTab(tableView,"search 1");
}

void ResultView::updateCurrentTabQuery(QStringList queryList)
{
	// delete the old model and replace with new model
	
	//QTableView *currentTableView = this
	// why?  from http://doc.trolltech.com/4.5/itemviews-addressbook.html
	QTableView *tempView = static_cast<QTableView*>(currentWidget());
	
	QItemSelectionModel *m = tempView->selectionModel();
	QSqlQueryModel *model = new QSqlQueryModel;

	QString query = "SELECT ";
	query.append(queryList.at(0));
	query.append(" FROM ");
	query.append(queryList.at(1));
	query.append(" WHERE ");
	query.append(queryList.at(2));

	QString connName = LhGlobals::Instance().getConnNameFromTableName(queryList.at(1));
	Q_ASSERT(connName.length() > 0);

	model->setQuery(query, QSqlDatabase::database(connName));
	tempView->setModel(model);
	// when does QTableView know to recalc the display?
	delete m;
}

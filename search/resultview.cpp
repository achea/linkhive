#include "resultview.h"
#include "lhglobals.h"

#include "lhtableview.h"
#include "renderlinkdelegate.h"
#include <QSqlQueryModel>
#include <QtGlobal>

ResultView::ResultView(QWidget *parent) : QTabWidget(parent)
{
	addBlankTab();
	connect(this, SIGNAL(currentChanged(int)), this, SLOT(sendCurrentTabQuery(int)));
}

void ResultView::addBlankTab()
{
	// add a new tab with QTableView with nothing
	QSqlQueryModel *model = new QSqlQueryModel;
	// the text for the query defaults to boring count 
	model->setQuery("SELECT COUNT(*) FROM reddit_stories", QSqlDatabase::database(LhGlobals::Instance().getConnNameFromTableName("reddit_stories")));
	LhTableView *tableView = new LhTableView;
	tableView->setItemDelegate(new RenderLinkDelegate);		// URL matcher
	tableView->setModel(model);
	tableView->setEditTriggers(QAbstractItemView::NoEditTriggers);

	// add a list so as to not have it empty
	QStringList list;
	list << "COUNT(*)" << "reddit_stories" << "true";
	tableView->saveQuery(list);

	// TODO proper tab count
	addTab(tableView,"search 1");
}

void ResultView::closeCurrentTab()
{
	// if only one tab, don't close
	if (this->count() <= 1)
		return;
	LhTableView *tempView = static_cast<LhTableView*>(widget(this->currentIndex()));
	this->removeTab(this->currentIndex());
	// FIXME memory leak ?  does deleting this delete childs?
	delete tempView;
}

void ResultView::updateCurrentTabQuery(QStringList queryList)
{
	// delete the old model and replace with new model
	
	//QTableView *currentTableView = this
	// why?  from http://doc.trolltech.com/4.5/itemviews-addressbook.html
	LhTableView *tempView = static_cast<LhTableView*>(currentWidget());
	
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
	tempView->saveQuery(queryList);
	// when does QTableView know to recalc the display?
	delete m;
}

void ResultView::sendCurrentTabQuery(int index)
{
	// TODO somehow to send blank QStringList if default "blank" tab
	LhTableView *tempView = static_cast<LhTableView*>(widget(index));
	QStringList tempList = tempView->getQuery();
	emit currentQueryChanged(tempList);
}

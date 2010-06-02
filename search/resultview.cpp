#include "resultview.h"
#include "lhglobals.h"

#include "lhtableview.h"
#include "renderlinkdelegate.h"
#include <QSqlQueryModel>
#include <QtGlobal>

ResultView::ResultView(QWidget *parent) : QTabWidget(parent)
{
	// TODO make these configurable
	QStringList list;
	list << "DISTINCT subreddit,COUNT(*) AS count" << "reddit_stories" << "1 GROUP BY subreddit ORDER BY count DESC";
	addQueryTab(list, "Subreddit Count");
	list.clear();
	list << "score,num_comments,title,permalink,url" << "reddit_stories" << "1 ORDER BY id DESC";
	addQueryTab(list, "Reddit Stories");
	list.clear();
	list << "score,comments,title,url,link" << "hn_stories" << "1 ORDER BY id DESC";
	addQueryTab(list, "HN Stories");
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
	list << "COUNT(*)" << "reddit_stories" << "1";
	tableView->saveQuery(list);

	// TODO proper tab count
	addTab(tableView,"search 1");
}

void ResultView::addQueryTab(const QStringList &queryList, const char tabTitle[])
{
	QSqlQueryModel *model = new QSqlQueryModel;

	// Construct the query
	QString query = "SELECT " + queryList.at(0) + " FROM " + queryList.at(1) + " WHERE " + queryList.at(2);
	model->setQuery(query, QSqlDatabase::database(LhGlobals::Instance().getConnNameFromTableName(queryList.at(1))));
	LhTableView *tableView = new LhTableView;
	tableView->setItemDelegate(new RenderLinkDelegate);		// URL matcher
	tableView->setModel(model);
	tableView->setEditTriggers(QAbstractItemView::NoEditTriggers);
	tableView->saveQuery(queryList);

	addTab(tableView, tabTitle);
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

void ResultView::selectTab(int direction)
{
	// move left or right
	// TODO enum
	Q_ASSERT(direction == -1 || direction == 1);

	int curIndex = this->currentIndex();
	int newIndex;
	if (curIndex < 0)		// -1 for no widgets
		return;
	curIndex += direction;
	if (curIndex < 0)
		newIndex = this->count() - 1;
	else if (curIndex > this->count() - 1)
		newIndex = 0;
	else
		newIndex = curIndex;
		
	this->setCurrentIndex(newIndex);
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

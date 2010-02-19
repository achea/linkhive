#include "lhtableview.h"
#include <QStringList>

void LhTableView::saveQuery(const QStringList& queryList)
{
	this->queryList = queryList;
}

const QStringList& LhTableView::getQuery()
{
	return this->queryList;
}


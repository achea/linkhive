#include "lhtableview.h"
#include "datatypes.h"
#include <QStringList>
#include <QDesktopServices>
#include <QUrl>
#include <QModelIndex>
#include <QRegExp>

LhTableView::LhTableView(QWidget *parent) : QTableView(parent)
{
	connect(this, SIGNAL( activated(const QModelIndex &)), this, SLOT( openIfURL(const QModelIndex &) ));
}

void LhTableView::saveQuery(const QStringList& queryList)
{
	this->queryList = queryList;
}

const QStringList& LhTableView::getQuery()
{
	return this->queryList;
}

void LhTableView::openIfURL(const QModelIndex &index)
{
	QString tempStr;
	if (qVariantCanConvert<QString>(index.data()))
	{
		QRegExp rex(URL_REGEXP);
		tempStr = index.data(Qt::DisplayRole).toString();
		if (!tempStr.isEmpty() && rex.indexIn(tempStr) != -1)
		{
			QDesktopServices::openUrl(QUrl(tempStr));
		}
	}
}

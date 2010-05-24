#include "lhtableview.h"
#include "datatypes.h"
#include "lhglobals.h"
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
	QMap<QString,QString> extraURLs = LhGlobals::Instance().extraURLs;

	QString curStr;
	if (qVariantCanConvert<QString>(index.data()))
	{
		QRegExp rex(URL_REGEXP);
		curStr = index.data(Qt::DisplayRole).toString();
		if (!curStr.isEmpty() && rex.indexIn(curStr) != -1)
		{
			QDesktopServices::openUrl(QUrl(curStr));
		}

		// now the custom URL regexs
		foreach (QString tempStr, extraURLs.keys())
		{
			rex.setPattern(tempStr);
			if (rex.indexIn(curStr) != -1)
			{
				QDesktopServices::openUrl(QUrl(extraURLs.value(tempStr) + curStr));
			}
		}
	}
}

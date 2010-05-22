#include "renderlinkdelegate.h"

#include "datatypes.h"		// For URL_REGEXP
#include <QString>
#include <QWidget>
#include <QPainter>
#include <QStyleOptionViewItem>
#include <QModelIndex>
#include <QRegExp>

RenderLinkDelegate::RenderLinkDelegate(QWidget *parent) : QStyledItemDelegate(parent)
{
}

void RenderLinkDelegate::paint(QPainter *painter, const QStyleOptionViewItem &option, const QModelIndex &index) const
{
	// check if current item is string, then if URL regex
	// http://stackoverflow.com/questions/2375763/how-to-open-an-url-in-a-qtableview
	QString tempStr;
	if (qVariantCanConvert<QString>(index.data()))
	{
		QRegExp rex(URL_REGEXP);
		tempStr = index.data(Qt::DisplayRole).toString();
		if (!tempStr.isEmpty() && rex.indexIn(tempStr) != -1)
		{
			painter->save();

			// state means once not that state, this stuff is not applied
			if (option.state & QStyle::State_MouseOver)		
			{
				QFont font = option.font;
				font.setUnderline(true);
				painter->setFont(font);
				painter->setPen(option.palette.link().color());
			}
			painter->drawText(option.rect, Qt::AlignLeft | Qt::AlignVCenter, tempStr);

			painter->restore();

			return;		// done; don't do the defaults
		}
	}
	
	// default
	QStyledItemDelegate::paint(painter, option, index);
}

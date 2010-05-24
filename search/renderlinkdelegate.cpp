#include "renderlinkdelegate.h"

#include "datatypes.h"		// For URL_REGEXP
#include "lhglobals.h"
#include <QString>
#include <QWidget>
#include <QPainter>
#include <QPalette>
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
	QString curStr;
	bool isURL = false;
	if (qVariantCanConvert<QString>(index.data()))
	{
		QRegExp rex(URL_REGEXP);
		curStr = index.data(Qt::DisplayRole).toString();
		if (!curStr.isEmpty() && rex.indexIn(curStr) != -1)
			isURL = true;
		else 		// if already isURL, don't need to check custom ones
		{
			// also the custom URLs
			foreach (QString tempStr, LhGlobals::Instance().extraURLs.keys())
			{
				rex.setPattern(tempStr);
				if (rex.indexIn(curStr) != -1)
					isURL = true;
			}
		}

		if (isURL)
		{
			painter->save();

			QFont font = option.font;
			font.setUnderline(true);
			painter->setFont(font);
			// state means once not that state, this stuff is not applied
			if (option.state & QStyle::State_MouseOver)			// MouseOver before Selected
			{
				painter->setPen(option.palette.link().color());
			}
			else if (option.state & QStyle::State_Selected)		
			{
				// TODO what is the default 3D looking way to do this?
				painter->fillRect(option.rect, option.palette.highlight());
				painter->setPen(option.palette.highlightedText().color());
			}
			// TODO draw something for QStyle::State_HasFocus
			painter->drawText(option.rect, Qt::AlignLeft | Qt::AlignVCenter, curStr);

			painter->restore();

			return;		// done; don't do the defaults
		}
	}
	
	// default
	QStyledItemDelegate::paint(painter, option, index);
}

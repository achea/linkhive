#ifndef RENDERLINKDELEGATE_H
#define RENDERLINKDELEGATE_H

#include <QStyledItemDelegate>
class QWidget;
class QPainter;
class QStyleOptionViewItem;
class QModelIndex;

class RenderLinkDelegate : public QStyledItemDelegate
{
	Q_OBJECT

	public:
		RenderLinkDelegate(QWidget *parent = 0);
		void paint(QPainter *painter, const QStyleOptionViewItem &option, const QModelIndex &index) const;
		//QSize sizeHint(const QStyleOptionViewItem &option, const QModelIndex &index) const;

	private:

};
#endif


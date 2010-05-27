#ifndef LHTABLEVIEW_H
#define LHTABLEVIEW_H
// basically to save QStringList query data
#include <QTableView>

class QStringList;
class QModelIndex;

class LhTableView : public QTableView
{
	Q_OBJECT

	public:
		LhTableView(QWidget* parent = 0);
		void saveQuery(const QStringList&);
		const QStringList& getQuery();

	private slots:
		void openIfURL(const QModelIndex &);

	private:
		QStringList queryList;
};
#endif

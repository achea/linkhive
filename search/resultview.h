#ifndef RESULTVIEW_H
#define RESULTVIEW_H
#include <QTabWidget>

class ResultView : public QTabWidget
{
	Q_OBJECT

	public:
		ResultView(QWidget *parent = 0);

	public slots:
		/// given QStringList from SearchPanel, update the current tab
		void updateCurrentTabQuery(QStringList);

	private:

};
#endif

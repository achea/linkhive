#ifndef RESULTVIEW_H
#define RESULTVIEW_H
#include <QTabWidget>

class ResultView : public QTabWidget
{
	Q_OBJECT

	public:
		ResultView(QWidget *parent = 0);
		void addBlankTab();			// not private since accessed by LhMainWindow
		void closeCurrentTab();

	signals:
		void currentQueryChanged(const QStringList&);

	public slots:
		/// given QStringList from SearchPanel, update the current tab
		void updateCurrentTabQuery(QStringList);

	private slots:
		// given int from currentChanged(), then extract the QStringList and emit a currentQueryChanged signal
		void sendCurrentTabQuery(int);

};
#endif

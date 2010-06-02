#ifndef RESULTVIEW_H
#define RESULTVIEW_H
#include <QTabWidget>

class ResultView : public QTabWidget
{
	Q_OBJECT

	public:
		ResultView(QWidget *parent = 0);

	signals:
		void currentQueryChanged(const QStringList&);

	public slots:
		/// given QStringList from SearchPanel, update the current tab
		void updateCurrentTabQuery(QStringList);
		void addBlankTab();			// not private since accessed by LhMainWindow
		void addQueryTab(const QStringList &, const char[]);
		void closeCurrentTab();
		void selectTab(int);			// -1 for left, 1 for right

	private slots:
		// given int from currentChanged(), then extract the QStringList and emit a currentQueryChanged signal
		void sendCurrentTabQuery(int);

};
#endif

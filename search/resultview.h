#ifndef RESULTVIEW_H
#define RESULTVIEW_H
#include <QTabWidget>

class QKeyEvent;

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

	private slots:
		// given int from currentChanged(), then extract the QStringList and emit a currentQueryChanged signal
		void sendCurrentTabQuery(int);

	private:
		void addBlankTab();
		void closeCurrentTab();

	protected:
		void keyPressEvent(QKeyEvent*);

};
#endif

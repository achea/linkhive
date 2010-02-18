#ifndef LHSETTINGS_H
#define LHSETTINGS_H

#include <QDialog>
#include <QWidget>
#include <QHash>

class QTabWidget;
class QShowEvent;
class QComboBox;
class QLineEdit;

class LhSettings : public QDialog
{
	Q_OBJECT

	public:
		LhSettings(QWidget *parent = 0);

	private slots:
		void saveAccept();
	private:
		QTabWidget *tabWidget;			// different tabs added here
		// upon opening the dialog, update the tabs's LhGlobals local copy
		void showEvent(QShowEvent *);
};

class TableTab : public QWidget
{
	Q_OBJECT

	public:
		TableTab(QWidget *parent = 0);
		// TODO typedef
		// in update, update the comboboxes and lineedits
		void updateConfigCopies(const QHash<QString, int>&, const QHash<int,QHash<QString,QString> >&);
		
	private slots:
		void updateTableChanged(const QString &);
	private:
		QHash<QString,int> tableNames;
		QHash<int, QHash<QString, QString> > connectionConfigs;

		QComboBox *tableComboBox;		// has list of tables tables
		QComboBox *configComboBox;		// has list of configurations of databases
		QComboBox *configDbType;
		QLineEdit *configDbHost;
		QLineEdit *configDbUser;
		QLineEdit *configDbPass;
		QLineEdit *configDbDb;

		void setCurrentDb(int);			// updates display
};
#endif

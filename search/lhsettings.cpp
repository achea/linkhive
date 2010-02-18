#include "lhsettings.h"
#include "lhglobals.h"
#include "datatypes.h"

#include <QtGlobal>
#include <QDebug>

#include <QTabWidget>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QVBoxLayout>
#include <QFormLayout>
#include <QLabel>
#include <QDialogButtonBox>
#include <QMessageBox>

#include <QGroupBox>
#include <QComboBox>
#include <QPushButton>
#include <QLineEdit>

LhSettings::LhSettings(QWidget *parent) : QDialog(parent)
{
	tabWidget = new QTabWidget;
	tabWidget->addTab(new TableTab(), tr("Tables"));

	QDialogButtonBox *buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);

	connect(buttonBox, SIGNAL(accepted()), this, SLOT(saveAccept()));		// what about in between?
	connect(buttonBox, SIGNAL(rejected()), this, SLOT(reject()));

	QVBoxLayout* mainLayout = new QVBoxLayout;
	mainLayout->addWidget(tabWidget);
	mainLayout->addWidget(buttonBox);

	setLayout(mainLayout);
}

void LhSettings::saveAccept()
{
	// save all settings
	QMessageBox::information(this,"You're done!","Configured! :)");
	this->accept();
}

void LhSettings::showEvent(QShowEvent *e)
{
	// does this get called if dialog minimized, then maximized?
	// position 0 is TableTab
	// plain widget() just returns QWidget; we want TableTab
	QMessageBox::information(this,"about to show","about to show");
	TableTab *tempTab = static_cast<TableTab*>(tabWidget->widget(0));
	tempTab->updateConfigCopies(LhGlobals::Instance().tableNames,LhGlobals::Instance().connectionConfigs);
	// TODO how to propery call parent class functions
	QDialog::showEvent(e);
}

/* TableTab */
// lets user enter database connection settings for each table (that stores data for social news site stories, or personal annotation notes, or --)
TableTab::TableTab(QWidget *parent) : QWidget(parent)
{
	// assume that the LhGlobals has already created tables
	// TODO typedefs to match so when need to change, only need to change in one typedef
	// TODO how to update on focus?
	// create a local copy, so that current isn't modified
	
	// tableGroup has the QComboBox and two QPushButtons
	QGroupBox *tableGroup = new QGroupBox(tr("Tables"));
	tableComboBox = new QComboBox;
	tableComboBox->setSizeAdjustPolicy(QComboBox::AdjustToContents);

	// TODO icons for pushbuttons
	QPushButton *tableAddButton = new QPushButton(tr("New"));
	QPushButton *tableDelButton = new QPushButton(tr("Delete"));
	QLabel *tableLabel1 = new QLabel(tr("Table:"));

	QHBoxLayout *tableLayout = new QHBoxLayout;
	tableLayout->addWidget(tableLabel1);
	tableLayout->addWidget(tableComboBox);
	tableLayout->addWidget(tableAddButton);
	tableLayout->addWidget(tableDelButton);
	tableLayout->addStretch();
	tableGroup->setLayout(tableLayout);

	// now the config group
	QGroupBox *configGroup = new QGroupBox(tr("Database configuration"));
	// two layouts in VBox, top is HBox and bottom is Grid
	configComboBox = new QComboBox;

	QPushButton *configSaveButton = new QPushButton(tr("Save"));
	QPushButton *configAddButton = new QPushButton(tr("New"));
	QPushButton *configDelButton = new QPushButton(tr("Delete"));
	QLabel *configLabel1 = new QLabel(tr("Config:"));
	connect(configSaveButton, SIGNAL(clicked()), this, SLOT(saveConfigLocal()));

	QHBoxLayout *layout1 = new QHBoxLayout;
	layout1->addWidget(configLabel1);
	layout1->addWidget(configComboBox);
	layout1->addWidget(configSaveButton);
	layout1->addWidget(configAddButton);
	layout1->addWidget(configDelButton);
	layout1->addStretch();

	// now the db form
	configDbType = new QComboBox;
	configDbHost = new QLineEdit;
	configDbUser = new QLineEdit;
	configDbPass = new QLineEdit;
	configDbDb = new QLineEdit;

	QFormLayout *configDbLayout = new QFormLayout;
	configDbLayout->addRow(tr("Type:"),configDbType);
	configDbLayout->addRow(tr("Host:"),configDbHost);
	configDbLayout->addRow(tr("User:"),configDbUser);
	configDbLayout->addRow(tr("Pass:"),configDbPass);
	configDbLayout->addRow(tr("Db:"),configDbDb);

	// the config group
	QVBoxLayout *configLayout = new QVBoxLayout;
	configLayout->addLayout(layout1);
	configLayout->addLayout(configDbLayout);
	configGroup->setLayout(configLayout);
	
	// the tab widget has both groups
	QVBoxLayout *mainLayout = new QVBoxLayout;
	mainLayout->addWidget(tableGroup);
	mainLayout->addWidget(configGroup);
	mainLayout->addStretch();
	setLayout(mainLayout);
	
	// set the configs for the first time (before the connect(), because combobox->addItem triggers currentIndexChanged, and setCurrentDb()'s findText will not find it)
	updateConfigCopies( LhGlobals::Instance().tableNames, LhGlobals::Instance().connectionConfigs);
	// activated instead of currentIndexChanged because don't want to be notified if programmatically changed.  Though, activated can trigger even if no change, but probably no problems with that
	// change back to currentIndexChanged because I think I squashed the bug (clear())
	connect(tableComboBox, SIGNAL(currentIndexChanged(const QString &)), this, SLOT(updateTableChanged(const QString &)));
	connect(configComboBox, SIGNAL(currentIndexChanged(const QString &)), this, SLOT(updateConnectionChanged(const QString &)));
	
}

void TableTab::updateConfigCopies(const QHash<QString, int>& tables, const QHash<int,QHash<QString,QString> >& configs)
{
	tableNames = tables;
	connectionConfigs = configs;

	// add to tableComboBox
	//tableComboBox->clear();		// a slot
		// don't clear, since currentIndexChanged will trigger with each addItem and "" isn't contained in tableNames
	QString name;
	foreach( name, tableNames.keys())
	{
		if (tableComboBox->findText(name) < 0)	// -1 if not found
			tableComboBox->addItem(name);
	}

	// add to configComboBox
	//configComboBox->clear();
	int configNum;
	foreach( configNum, connectionConfigs.keys())
	{
		name = CONNECTION_PREFIX;
		name += QString::number(configNum);
		// FIXME but even though same config number, might be different data
		if (configComboBox->findText(name) < 0)		// only add if not found
			configComboBox->addItem(name); 
	}

	// update 
	name = tableComboBox->currentText();
	this->updateTableChanged(name);
}

void TableTab::updateTableChanged(const QString& name)
{
	// name is the id
	Q_ASSERT(tableNames.contains(name));
	int configNum = tableNames.value(name);

	this->setCurrentDb(configNum);
}

// given a connection id, display the text
void TableTab::setCurrentDb(int connectionId)
{
	// update comboboxes and lineedits
	// assume combobox has all the connection names
	// now have to display the right one
	// get the index of the combobox with the CONNECTION_PREFIX+connectionId text
	QString name = CONNECTION_PREFIX;
	name += QString::number(connectionId);
	int index = configComboBox->findText(name);
	Q_ASSERT(index >= 0);		// -1 if not found

	configComboBox->setCurrentIndex(index);
	Q_ASSERT(connectionConfigs.contains(connectionId));
	// TODO typedef
	QHash<QString, QString> config = connectionConfigs.value(connectionId);
	configDbHost->setText(config.value("host"));
	configDbUser->setText(config.value("user"));
	configDbPass->setText(config.value("pass"));
	configDbDb->setText(config.value("db"));
}

void TableTab::updateConnectionChanged(const QString& name)
{
	// unlike updateTableChanged, the only reliable identifier is the number at the end of the name string
	// so extract it and cast to int
	QString connString = name;
	connString.replace(CONNECTION_PREFIX,"");
	//qDebug() << "name : " << name << " conn : " << connString;
	bool status;
	this->setCurrentDb(connString.toInt(&status));
	Q_ASSERT(status);
}

void TableTab::saveConfigLocal()
{
	// user requested that the current host, user, etc be saved to the current connection (identified by the combobox)
	QString connName = configComboBox->currentText();
	connName.replace(CONNECTION_PREFIX,"");
	bool status;
	int connId = connName.toInt(&status);
	Q_ASSERT(status);

	QHash<QString, QString> tempConfig;
	tempConfig.insert("host",configDbHost->text());
	tempConfig.insert("user",configDbUser->text());
	tempConfig.insert("pass",configDbPass->text());
	tempConfig.insert("db",configDbDb->text());

	// assume QHash only allows one value per key
	connectionConfigs.insert(connId,tempConfig);

	// also this connection id for the current table
	QString curTable = tableComboBox->currentText();
	Q_ASSERT(tableNames.contains(curTable));
	tableNames.insert(curTable,connId);
}

void TableTab::saveConfigGlobal()
{
}

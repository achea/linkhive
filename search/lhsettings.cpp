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
	// TODO change on updateConfigCopies, so looks nicer
	tableComboBox->setMinimumWidth(150);	// because the text isn't setting the minimum for us

	// TODO icons for pushbuttons
	QPushButton *tableAddButton = new QPushButton(tr("Add"));
	QPushButton *tableDelButton = new QPushButton(tr("Delete"));
	QLabel *tableLabel1 = new QLabel(tr("Table:"));

	QHBoxLayout *tableLayout = new QHBoxLayout;
	tableLayout->addWidget(tableLabel1);
	tableLayout->addWidget(tableComboBox);
	tableLayout->addWidget(tableAddButton);
	tableLayout->addWidget(tableDelButton);
	tableGroup->setLayout(tableLayout);

	// now the config group
	QGroupBox *configGroup = new QGroupBox(tr("Database configuration"));
	// two layouts in VBox, top is HBox and bottom is Grid
	configComboBox = new QComboBox;

	QPushButton *configAddButton = new QPushButton(tr("Add"));
	QPushButton *configDelButton = new QPushButton(tr("Delete"));
	QLabel *configLabel1 = new QLabel(tr("Config:"));

	QHBoxLayout *layout1 = new QHBoxLayout;
	layout1->addWidget(configLabel1);
	layout1->addWidget(configComboBox);
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
	connect(tableComboBox, SIGNAL(currentIndexChanged(const QString &)), this, SLOT(updateTableChanged(const QString &)));
	
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
	configComboBox->clear();
	int configNum;
	foreach( configNum, connectionConfigs.keys())
	{
		name = CONNECTION_PREFIX;
		name += QString::number(configNum);
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

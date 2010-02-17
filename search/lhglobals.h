#ifndef LHGLOBALS_H
#define LHGLOBALS_H
// global to initialize databases, and read/write settings

#include <QHash>
class QString;

class LhGlobals
{
	public:
		static LhGlobals& Instance()
		{
			static LhGlobals singleton;
			return singleton;
		}

		// Linkhive globals
		// the ints are all the same; they reference the db connection
		QHash<QString,int> tableNames;					// tablename : configid
		QHash<int,QHash<QString,QString> > connectionConfigs;		// for each connection, there is host/user/pass/db
		QHash<int,QString> connectionNames;				// configid : connname

		bool readSettings();
		bool createConnections();
		bool closeAllDbs();
		QString getConnNameFromTableName(QString);
			// returns empty string if error
			// should I throw exception?
			// return pointers instead?

		// Other non-static member functions
	private:
		LhGlobals() {}                                  // Private constructor
		~LhGlobals() {}
		LhGlobals(const LhGlobals&);                 // Prevent copy-construction
		LhGlobals& operator=(const LhGlobals&);      // Prevent assignment
};
#endif

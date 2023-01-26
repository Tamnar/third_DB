#!/usr/bin/env python3

# import psycopg2
# import psycopg2.sql
# import psycopg2.extensions
import Lab.utils

from . import DynamicSearch
from .AutoSchema import *


class LoanTable(SchemaTable):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.primary_key_name = f"id"

	def randomFill(self, instances=None, *args, **kwargs):
		if instances is None:
			instances = 100

		sql = f"""
		INSERT INTO "Library"."Loan"("UserID", "BookID", "LoanDate", "ReturnDate", "DesiredReturnDate")
		SELECT
		(SELECT "id" FROM "Library"."Users" ORDER BY random()*q LIMIT 1),
		(SELECT "id" FROM "Library"."Books" ORDER BY random()*q LIMIT 1),

		timestamp '2020-01-01' + random() * (timestamp '2020-11-11' - timestamp '2020-01-01'),
		timestamp '2021-01-01' + random() * (timestamp '2021-11-11' - timestamp '2021-01-01'),
		timestamp '2021-01-01' + random() * (timestamp '2021-11-11' - timestamp '2021-01-01')
		FROM
		(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters),
		generate_series(1, {instances}) as q;

		"""
		super().randomFill(*args, **kwargs, sql_replace=sql)


class Library(Schema):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._dynamicsearch = {a.name: a for a in [DynamicSearch.BookDynamicSearch(self), DynamicSearch.UserLoanDynamicSearch(self)]}
		# self.reoverride()

	def reoverride(self):
		# Table override
		self._tables.Loan = LoanTable(self, f"Loan")

	def reinit(self):
		# sql = f"""
		# 	SELECT table_name FROM information_schema.tables
		# 	WHERE table_schema = '{self}';
		# """
		with self.dbconn.cursor() as dbcursor:
			# dbcursor.execute(sql)
			for a in self.refresh_tables():  # tuple(dbcursor.fetchall()):
				q = f"""DROP TABLE IF EXISTS {a} CASCADE;"""
				# print(q)
				dbcursor.execute(q)

		tables = [
			f"""CREATE SCHEMA IF NOT EXISTS "{self}";""",
			f"""CREATE TABLE IF NOT EXISTS "{self}"."Authors" (
				id bigserial,
				"Name" character varying(127) NOT NULL,
				CONSTRAINT "Authors_pkey" PRIMARY KEY (id)
				-- UNIQUE("Name")
			);
			""",
			f"""CREATE TABLE IF NOT EXISTS "{self}"."BooksData" (
				id bigserial,
				"AuthorID" bigint NOT NULL,
				"Name" character varying(127) NOT NULL,
				"PubYear" timestamp with time zone NOT NULL,
				"Price" money,
				CONSTRAINT "BooksData_pkey" PRIMARY KEY (id),
				CONSTRAINT "BooksData_AuthorID_fkey" FOREIGN KEY ("AuthorID")
					REFERENCES "{self}"."Authors" (id) MATCH SIMPLE
					ON UPDATE NO ACTION
					ON DELETE CASCADE
					NOT VALID
			);
			""",
			f"""CREATE TABLE IF NOT EXISTS "{self}"."Books" (
				id bigserial,
				"DataID" bigint NOT NULL,
				CONSTRAINT "Books_pkey" PRIMARY KEY (id),
				CONSTRAINT "Books_DataID_fkey" FOREIGN KEY ("DataID")
					REFERENCES "{self}"."BooksData" (id) MATCH SIMPLE
					ON UPDATE NO ACTION
					ON DELETE CASCADE
					NOT VALID
			);
			""",
			f"""CREATE TABLE IF NOT EXISTS "{self}"."Users" (
					id bigserial,
					"Name" character varying(63) NOT NULL,
					"Surname" character varying(63) NOT NULL,
					"Patronymic" character varying(63) NOT NULL,
					"Address" character varying(255) NOT NULL,
					CONSTRAINT "Users_pkey" PRIMARY KEY (id)
			);
			""",
			f"""CREATE TABLE IF NOT EXISTS "{self}"."Loan" (
				id bigserial,
				"UserID" bigint NOT NULL,
				"BookID" bigint NOT NULL,
				"LoanDate" timestamp with time zone,
				"ReturnDate" timestamp with time zone,
				"DesiredReturnDate" timestamp with time zone,
				CONSTRAINT "Loan_pkey" PRIMARY KEY (id),
				CONSTRAINT "Loan_BookID_fkey" FOREIGN KEY ("BookID")
					REFERENCES "{self}"."Books" (id) MATCH SIMPLE
					ON UPDATE NO ACTION
					ON DELETE CASCADE
					NOT VALID,
				CONSTRAINT "Loan_UserID_fkey" FOREIGN KEY ("UserID")
					REFERENCES "{self}"."Users" (id) MATCH SIMPLE
					ON UPDATE NO ACTION
					ON DELETE CASCADE
					NOT VALID
			);
			""",
		]

		with self.dbconn.cursor() as dbcursor:
			for a in tables:
				dbcursor.execute(a)

		self.dbconn.commit()

		self.refresh_tables()
		# self.reoverride()

	def randomFill(self):
		self.tables.Authors.randomFill(5_000)
		self.tables.Users.randomFill(10_000)
		self.tables.BooksData.randomFill(1_000)
		self.tables.Books.randomFill(50_000)
		self.tables.Loan.randomFill(10_000)

	# def dynamicsearch(self):
	# 	result = Lab.utils.LabConsoleInterface({
	# 		"Books": lambda: DynamicSearch.BookDynamicSearch(self),
	# 		"UsersLoan": lambda: DynamicSearch.UserLoanDynamicSearch(self),
	# 		"return": lambda: Lab.utils.menuReturn(f"User menu return"),
	# 	}, promt = f"""Schema "{self}" dynamic search interface""")
	# 	return result


def _test():
	pass


if __name__ == "__main__":
	_test()

#!/usr/bin/env python
import itertools
import pprint

from .dynamicsearch import *

__all__ = ["BookDynamicSearch", "UserLoanDynamicSearch"]


class BookDynamicSearch(DynamicSearchBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = "Books"
		self.search: dict[self.SearchCriterias[CompareConstant]] = {
			"Author": SearchCriterias(f'"c"."Name"', f"Author", "varchar"),
			"Name": SearchCriterias(f'"b"."Name"', f"Name", "varchar"),
			"PubYear": SearchCriterias(f'"b"."PubYear"', f"PubYear", "timestamp"),
			"Price": SearchCriterias(f'"b"."Price"', f"Price", "money"),
		}
		# pprint.pprint(self.search)
		# self.selectcompositors = tuple(SelectCompositor(self.search[x], x) for a in self.search)
		# **{f"{a}": (lambda x: lambda: SelectCompositor(self.search[x], x))(a) for a in self.search},

	@property
	def sql(self):
		where = self.where
		sql = f"""
			SELECT
				"c"."Name" as "Author",

				"b"."Name" as "Name",
				"b"."PubYear" as "PubYear",
				"b"."Price" as "Price"

			FROM
				"{self.schema}"."Books" as "a"
				INNER JOIN "{self.schema}"."BooksData" as "b"
					ON "a"."DataID" = "b"."id"
				INNER JOIN "{self.schema}"."Authors" as "c"
					ON "b"."AuthorID" = "c"."id"
			{f'''WHERE
				{where};''' if where else f";"}
		"""

		return sql


class UserLoanDynamicSearch(DynamicSearchBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.name: str = "UsersLoan"
		self.search: dict[self.SearchCriterias[CompareConstant]] = {
			"Name": SearchCriterias(f'"a"."Name"', f"Name", "varchar"),
			"Surname": SearchCriterias(f'"a"."Surname"', f"Surname", "varchar"),
			"Patronymic": SearchCriterias(f'"a"."Patronymic"', "Patronymic", "varchar"),
			"Address": SearchCriterias(f'"a"."Address"', f"Address", "varchar"),

			"LoanDate": SearchCriterias(f'"b"."LoanDate"', f"LoanDate", "timestamp"),
			"ReturnDate": SearchCriterias(f'"b"."ReturnDate"', f"ReturnDate", "timestamp"),
			"DesiredReturnDate": SearchCriterias(f'"b"."DesiredReturnDate"', f"DesiredReturnDate", "timestamp"),

			"BookName": SearchCriterias(f'"d"."Name"', f"BookName", "varchar"),
		}

	@property
	def sql(self):
		where = self.where
		sql = f"""
			SELECT
				"a"."Name" as "Name",
				"a"."Surname" as "Surname",
				"a"."Patronymic" as "Patronymic",
				"a"."Address" as "Address",

				"b"."LoanDate" as "LoanDate",
				"b"."ReturnDate" as "ReturnDate",
				"b"."DesiredReturnDate" as "DesiredReturnDate",

				"d"."Name" as "BookName"

			FROM
				"{self.schema}"."Users" as "a"
				INNER JOIN "{self.schema}"."Loan" as "b"
					ON "a"."id" = "b"."UserID"
				INNER JOIN "{self.schema}"."Books" as "c"
					ON "b"."BookID" = "c"."id"
				INNER JOIN "{self.schema}"."BooksData" as "d"
					ON "c"."DataID" = "d"."id"
			{f'''WHERE
				{where};''' if where else f";"}
		"""

		return sql


def _test():
	pass


if __name__ == "__main__":
	_test()

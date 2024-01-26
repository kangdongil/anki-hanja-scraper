import os
import sqlite3
from typing import List, Tuple, Dict, Optional, Union


class SQLiteDB:
    """
    SQLite database context manager.

    :param db_path: Path to the SQLite database file.
    :type db_path: str
    """

    def __init__(self, db_path: str):
        """
        Initialize the SQLiteDB instance.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        """
        self.path = db_path
        self._check_db_exist()
        self.connections = []  # Prevent Overwritten Connection When nested

    def _check_db_exist(self):
        """Check if the SQLite database file exists."""
        if not os.path.isfile(self.path):
            raise ValueError(f"The database file '{self.path}' does not exist.")

    def __enter__(self):
        """
        Class Method which is called when entering a 'with' block and returns connection and cursor.

        :return: Tuple containing the SQLite connection and cursor.
        :rtype: tuple
        """
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        self.connections.append((conn, cursor))
        return conn, cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Class Method which is called when exiting the 'with' block when there is no exception

        :param exc_type: Type of the exception (or None if no exception).
        :type exc_type: type
        :param exc_value: The exception value (or None if no exception).
        :param traceback: The traceback object (or None if no exception).

        :return: True if no exception should propagate, False otherwise.
        :rtype: bool
        """
        if self.connections:
            conn, _ = self.connections.pop()
            if exc_type is None:
                conn.commit()
            else:
                conn.rollback()
            conn.close()

        return exc_type is None

    def run_query(self, query: str, parameters: Optional[Tuple] = ()) -> List[Tuple]:
        """
        Execute an SQL query and return the result.

        :param query: SQL query to be executed.
        :type query: str
        :param parameters: Parameters to be substituted into the query (default is an empty tuple).
        :type parameters: tuple, optional

        :return: List of tuples representing the query result.
        :rtype: List[Tuple]
        """
        with self as (conn, cursor):
            cursor.execute(query, parameters)
            result = cursor.fetchall()
        return result


class SQLiteTable:
    """
    Initialize the SQLiteTable instance.

    :param db: SQLiteDB instance.
    :type db: SQLiteDB
    :param tb_name: Name of the table.
    :type tb_name: str
    :param schema: Table schema defined as a dictionary.
    :type schema: Dict[str, str]
    """

    def __init__(
        self, db: SQLiteDB, tb_name: str, schema: Optional[Dict[str, str]] = None
    ):
        self.db = db
        self.name = tb_name
        self.schema = schema
        self._validate_schema()
        self._assign_table()

    def create_data(self, data: Dict[str, Union[int, str]]):
        """
        Create a new record in the table.

        :param data: Data for the new record.
        :type data: Dict[str, Union[int, str]]
        """
        columns = ", ".join(data.keys())
        values = ", ".join(["?" for _ in data])

        query = f"INSERT INTO {self.name} ({columns}) VALUES ({values})"
        try:
            self.db.run_query(query, tuple(data.values()))
        except sqlite3.IntegrityError as e:
            # Handle unique constraint violation
            if "UNIQUE constraint failed" in str(e):
                print(f"The data already exists in DB({self.db.path})")
                user_response = input(
                    "Do you want to update the existing record? (y/n): "
                ).lower()

                if user_response in ["y", ""]:
                    try:
                        # Attempt to update the existing record
                        self.update_data(data, {"hanja": data["hanja"]})
                    except ValueError as update_error:
                        print(f"Error updating data: {update_error}")
                else:
                    print("Aborting procedure. No changes made.")
            else:
                print(f"Error: {e}")

    def read_data(
        self,
        select_list: Union[List[str], str] = "*",
        where_condition: Optional[Dict[str, Union[int, str]]] = None,
        order_by_expression: Optional[str] = None,
        order_by_direction: Optional[str] = None,
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Retrieve records from the table based on the given conditions.

        :param select_list: List of columns to select or '*' to select all columns.
        :type select_list: Union[list, str]
        :param where_condition: Conditions to filter records.
        :type where_condition: Dict[str, Union[int, str]], optional
        :param order_by_expression: Column to use for sorting the result.
        :type order_by_expression: str, optional
        :param order_by_direction: Sorting direction ('ASC' or 'DESC').
        :type order_by_direction: str, optional

        :return: List of dictionaries representing the records.
        :rtype: List[Dict[str, Union[int, str]]]
        """

        # Helper function to validate columns
        def validate_columns(columns):
            for column in columns:
                if column.lower() != "*" and column.lower() not in self.schema:
                    raise ValueError(f"No such column: {column}")

        # Validate select_list
        if isinstance(select_list, list):
            validate_columns(select_list)
            select_list = ", ".join(select_list)
        elif isinstance(select_list, str):
            columns = [col.strip() for col in select_list.split(",")]
            validate_columns(columns)
            select_list = ", ".join(columns)
        else:
            raise ValueError(
                "Invalid select_list format. Should be a list or a string."
            )

        # Validate where_condition
        if where_condition and not isinstance(where_condition, dict):
            raise ValueError("where_condition must be a dictionary")

        where_clause, where_values = "", ()
        if where_condition:
            where_clause = "WHERE " + " AND ".join(
                [f"{column} = ?" for column in where_condition.keys()]
            )
            where_values = tuple(where_condition.values())

        # Validate order_by_expression
        if order_by_expression:
            # Attempt to execute a query with the ORDER BY expression to catch any errors
            try:
                self.db.run_query(
                    f"SELECT * FROM {self.name} ORDER BY {order_by_expression} LIMIT 1"
                )
            except sqlite3.Error as e:
                raise ValueError(f"Invalid ORDER BY expression: {e}")

        # Construct the SELECT statement
        select_clause = f"SELECT {select_list}"
        order_by_clause = (
            f"ORDER BY {order_by_expression} {order_by_direction}"
            if order_by_expression
            else ""
        )

        query = f"{select_clause} FROM {self.name} {where_clause} {order_by_clause}"

        # Execute the query
        return self.db.run_query(query, where_values)

    def update_data(
        self,
        new_data: Dict[str, Union[int, str]],
        where_condition: Optional[Dict[str, Union[int, str]]] = None,
    ):
        """
        Update records in the table based on the given conditions.

        :param new_data: Updated data for the records.
        :type new_data: Dict[str, Union[int, str]]
        :param where_condition: Conditions to identify records to be updated.
        :type where_condition: Dict[str, Union[int, str]], optional
        """
        # Validate that new_data is a dictionary
        if not isinstance(new_data, dict):
            raise ValueError("new_data must be a dictionary")

        # Validate that where_condition is a dictionary
        if where_condition and not isinstance(where_condition, dict):
            raise ValueError("where_condition must be a dictionary")

        # Construct the SET clause for the UPDATE statement
        set_clause = ", ".join([f"{column} = ?" for column in new_data.keys()])

        # Construct the WHERE clause for the UPDATE statement
        where_clause = ""
        if where_condition:
            where_clause = " AND ".join(
                [f"{column} = ?" for column in where_condition.keys()]
            )

        # Construct the UPDATE statement
        query = f"UPDATE {self.name} SET {set_clause} WHERE {where_clause}"

        try:
            # Execute the UPDATE statement
            self.db.run_query(
                query,
                tuple(new_data.values()) + tuple(where_condition.values())
                if where_condition
                else (),
            )
        except sqlite3.Error as e:
            print(f"Error updating data: {e}")

    def _validate_schema(self):
        """
        Validate the provided table schema.

        If `self.schema` is None, retrieves the existing schema from the database.
        Ensures that schema is a dictionary and contains at least one item.
        Validates the schema by ensuring that all columns have valid data types.

        :raises ValueError: If the schema is invalid.
        :return: True if the schema is successfully validated or retrieved.
        :rtype: bool
        """
        if self.schema is None:
            # Retrieve the existing schema from the database
            self.schema = self._get_existing_schema()
            return True

        # Ensure that schema is a dictionary and contains at least one item
        if not isinstance(self.schema, dict) or not self.schema:
            raise ValueError("Invalid schema. It should be a non-empty dictionary.")

        # Validate the schema by ensuring that all columns have valid data types
        data_types = {"INTEGER", "TEXT", "REAL", "BLOB", "NULL"}
        valid_columns = set()

        for column, options in self.schema.items():
            # Check if the column type is valid
            data_type = options.split()[0]
            if data_type not in data_types:
                raise ValueError(
                    f"Invalid data type '{data_type}' for column '{column}' in the table schema."
                )
            valid_columns.add(column.lower())  # Use lowercase names

        # Check if all columns in the schema are valid
        schema_columns = set(column.lower() for column in self.schema.keys())
        invalid_columns = schema_columns - valid_columns
        if invalid_columns:
            raise ValueError(
                f"Invalid columns in the schema: {', '.join(invalid_columns)}"
            )

        return True

    def _create_table(self):
        """
        Create the table in the SQLite database.

        Uses the provided schema to construct the CREATE TABLE SQL statement and execute it.

        :raises ValueError: If an error occurs during table creation.
        """
        with self.db as (_, cursor):
            # Construct the CREATE TABLE SQL statement
            columns_str = ", ".join(
                [f"{column} {options}" for column, options in self.schema.items()]
            )
            query = f"CREATE TABLE IF NOT EXISTS {self.name} ({columns_str})"

            # Execute the SQL statement
            cursor.execute(query)

    def _get_existing_schema(self):
        """
        Retrieve the existing schema of the table from the SQLite database.

        :return: Dictionary representing the existing schema.
        :rtype: Dict[str, str]

        :raises ValueError: If an error occurs while fetching the existing schema.
        """
        with self.db as (_, cursor):
            # Get the SQL statement used to create the table from sqlite_master
            cursor.execute(
                f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
                (self.name,),
            )
            query = cursor.fetchone()

            if query:
                # Extract the part of the SQL statement that defines the columns
                columns_definition = query[0].split("(")[1].split(")")[0].strip()
                columns_list = [col.strip() for col in columns_definition.split(",")]

                # Construct the existing schema dictionary
                existing_schema = {}
                for col in columns_list:
                    parts = col.split(" ")
                    col_name = parts[0]
                    col_type = " ".join(parts[1:])
                    existing_schema[col_name] = col_type

                return existing_schema

            else:
                raise ValueError(f"The table '{self.name}' does not exist.")

    def _are_schemas_compatible(self, existing_schema, provided_schema):
        """
        Check if the provided schema is compatible with the existing schema.

        :param existing_schema: Existing schema retrieved from the database.
        :type existing_schema: Dict[str, str]
        :param provided_schema: Schema provided during table instantiation.
        :type provided_schema: Dict[str, str]

        :raises ValueError: If schemas are not compatible.
        :return: True if schemas are compatible, False otherwise.
        :rtype: bool
        """
        if existing_schema != provided_schema:
            existing_columns = set(existing_schema.keys())
            provided_columns = set(provided_schema.keys())

            # Identify columns present in the provided schema but not in the existing schema
            new_columns = provided_columns - existing_columns
            if new_columns:
                raise ValueError(
                    f"The provided schema has new columns: {', '.join(new_columns)}"
                )

            # Identify columns present in the existing schema but not in the provided schema
            missing_columns = existing_columns - provided_columns
            if missing_columns:
                raise ValueError(
                    f"The provided schema is missing columns: {', '.join(missing_columns)}"
                )

            # Identify columns with different data types in the provided and existing schemas
            different_data_types = {
                column: (existing_schema[column], provided_schema[column])
                for column in existing_columns & provided_columns
                if existing_schema[column] != provided_schema[column]
            }

            if different_data_types:
                messages = [
                    f"Column '{column}' has different data types: Existing: {existing_schema[column]}, Provided: {provided_schema[column]}"
                    for column in different_data_types
                ]
                raise ValueError("\n".join(messages))
            # Schemas are compatible if no differences are found
            return True
        return True

    def _assign_table(self):
        """
        Assign the table to the SQLite database.

        Check if the table already exists. If not, create it using the provided schema.
        If the table exists, validate the compatibility of the existing schema with the provided schema.

        :raises ValueError: If an error occurs during table assignment.
        """
        with self.db as (_, cursor):
            # Check if the table already exists
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (self.name,),
            )
            existing_table = cursor.fetchone()

            if existing_table is None:
                # Table does not exist, create it
                if self.schema is not None:
                    self._create_table()
                else:
                    raise ValueError(
                        f"The table '{self.name}' does not exist, and schema is not provided."
                    )

            else:
                # Table exists
                existing_schema = self._get_existing_schema()
                if self.schema is not None:
                    # Schema is provided, check for compatibility
                    if not self._are_schemas_compatible(existing_schema, self.schema):
                        raise ValueError(
                            "The provided schema is not compatible with the existing table."
                        )


# Schema Definition for the 'hanjas' table
hanja_schema = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "hanja": "TEXT NOT NULL UNIQUE",
    "meaning": "TEXT NOT NULL",
    "meaning_official": "TEXT",
    "radical": "TEXT",
    "stroke_count": "INTEGER",
    "formation_letter": "TEXT",
    "grade": "INTEGER",
    "usage": "TEXT",
    "unicode": "TEXT",
    "reference_idx": "TEXT",
    "naver_dict_update_date": "TEXT",
    "naver_hanja_id": "TEXT",
}

# Sample hanja data
hanja_data = {
    "hanja": "示",
    "meaning": "볼 시",
    "meaning_official": "볼 시",
    "radical": "⺭",
    "stroke_count": 5,
    "formation_letter": "二+小",
    "grade": 5,
    "usage": "중학용,읽기5급,쓰기4급,대법원인명용",
    "unicode": "U+793A",
    "reference_idx": "1_137",
    "naver_dict_update_date": "2024-01-21",
    "naver_hanja_id": "2367ab9f300841eebcb8a76db1f91654",
}

# Create SQLiteDB and SQLiteTable Instances
hanja_db = SQLiteDB("data/db/hanja.db")
hanja_table = SQLiteTable(hanja_db, "hanjas", hanja_schema)

""" # Insert a row into the 'hanjas' table
hanja_table.create_data(hanja_data)

# Retrieve all rows from the 'hanjas' table
result = hanja_table.read_data(["hanja", "meaning", "grade"])
print(result) """

# Update a record in 'hanjas' table
hanja_table.update_data({"meaning": "빌 시", "stroke_count": 3}, {"hanja": "示"})
print(hanja_table.read_data(select_list=["id", "hanja", "meaning"]))

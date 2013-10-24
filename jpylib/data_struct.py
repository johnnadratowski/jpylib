'''
Contains extension of python dictionary objects

Created on Jan 11, 2012

@author: john
'''
import datetime, logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class DynamicObject(object):
    """
    Object that does not throw exceptions when working with attributes that it does not
    currently contain.  Can specify a default for attributes that do not exist.
    """
    def __init__(self, default=None, **kwargs):
        self._default=default
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __getattr__(self, item):
        return self._default

    def __delattr__(self, item):
        try:
            delattr(self, item)
        except AttributeError:
            pass

class AttrDict(dict):
    """
    Dictionary class that allows for dot notation when accessing members.
    If dict contains sub-dicts, those dicts will be converted to AttrDict
    so that the sub members can be accessed using dot notation as well.
    Example: dict1.dict2.value
    """

    def __init__(self, initial=None, dict_default=None, **kwargs):
        super(AttrDict, self).__setattr__('_dict_default', dict_default)
        super(AttrDict, self).__init__(initial or {}, **kwargs)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return self._dict_default if '_dict_default' in self.__dict__ else None

    def __setitem__(self, key, value):
        if type(value) == dict:
            # Make so sub-dicts can be accessed using dot notation
            value = AttrDict(value)
        super(AttrDict, self).__setitem__(key, value)

    def __setattr__(self, key, value):
        if key in dir(self):
            super(AttrDict, self).__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def __delattr__(self, item):
        if item in dir(self):
            super(AttrDict, self).__delattr__(item)
        else:
            self.__delitem__(item)

    def add_member(self, name, value):
        """
        To get around default setattr behavior to add a member such as a method to this class,
        you can call this method.
        """
        super(AttrDict, self).__setattr__(name, value)

class DataTable(object):

    class DataColumn(AttrDict):

        def __init__(self, table, dict_default='', data=None, **kwargs):
            self.table = table

            super(DataTable.DataColumn, self).__init__(
                initial=data, dict_default=dict_default, **kwargs
            )

        @property
        def cells(self):
            return [cell for _, cell in self]

        def get_default_value(self, value):
            if self.default_value:
                return self.default_value
            elif self.table.meta.default_value:
                return self.table.default_value
            elif self.type == "decimal":
                return Decimal()
            elif self.type == "int" or self.type == "long":
                return 0
            elif self.type == "bool" or self.type == "string":
                return ''
            else:
                return value

        def index(self):
            return self.table.columns.indexOf(self)

        def __iter__(self):
            for row in self.table.rows:
                for cell in row.cells:
                    if cell.column == self:
                        yield row, cell

    class DataRow(AttrDict):

        def __init__(self, table, data_obj, cells=None, dict_default='', data=None, **kwargs):
            self.table = table
            self.data_obj = data_obj
            self.cells = cells or ()

            super(DataTable.DataRow, self).__init__(
                initial=data, dict_default=dict_default, **kwargs
            )

        def get_date_cell(self):
            for cell in self.cells:
                if cell.type == "date" or cell.type == "datetime":
                    return cell
            return None

        def index(self):
            return self.table.all_rows.indexOf(self)

        def __iter__(self):
            return (cell for cell in self.cells)

    class DataCell(AttrDict):

        def __init__(self, table, row, column, dict_default='', data=None, **kwargs):
            self.table = table
            self.row = row
            self.column = column

            super(DataTable.DataCell, self).__init__(
                initial=data, dict_default=dict_default, **kwargs
            )

        @property
        def prefix(self):
            return self.column.prefix or ''

        @property
        def suffix(self):
            return self.column.suffix or ''

        @property
        def precision(self):
            return self.column.precision or 2

        @property
        def type(self):

            if isinstance(self.value, datetime.datetime):
                return "datetime"
            elif isinstance(self.value, datetime.date):
                return "date"
            elif isinstance(self.value, Decimal):
                return "decimal"
            elif isinstance(self.value, int):
                return "int"
            elif isinstance(self.value, long):
                return "long"
            elif isinstance(self.value, type(None)):
                return "null"
            elif isinstance(self.value, basestring):
                return "string"
            elif isinstance(self.value, bool):
                return "bool"
            else:
                raise TypeError("Unknown type specified for DataCell")

        def index(self):
            return self.row.cells.indexOf(self)

    def __init__(self, data_objects, columns, total_data_object=None,
                 table_meta=None, row_meta=None, cell_meta=None):

        self.data_objects = data_objects
        self.total_data_object = total_data_object

        self._table_meta = table_meta or {}
        self._row_meta = row_meta or {}
        self._cell_meta = cell_meta or {}
        self.meta = AttrDict(self._table_meta)

        self.columns = tuple([self._build_column(column) for column in columns])

        self._build_table()

    @property
    def columns_by_name(self):
        return {col.name: col for col in self.columns if col.name}

    @property
    def cells(self):
        return [cell for _, _, cell in self]

    def _build_table(self):

        rows = []
        for data_obj in self.data_objects:
            row = self._build_row(data_obj)
            row.cells = tuple([self._build_cell(row, column, data_obj) for column in self.columns])
            rows.append(row)

        self.rows = tuple(rows)

        self._build_total()

    def _build_total(self):
        self.total_row = None
        if self.total_data_object:
            self.total_row = self._build_total_row(self.total_data_object)
            cells = tuple([self._build_total_cell(self.total_row, column,
                                                  self.total_data_object)
                           for column in self.columns])
            self.total_row.cells = cells

            self.all_rows = tuple(self.rows + (self.total_row,))

        else:
            self.all_rows = tuple(self.rows)

    def _build_column(self, column):
        return self.DataColumn(self, data=column)

    def _build_total_row(self, data_obj, cells=None):
        return self._build_row(data_obj, cells=cells)

    def _build_row(self, data_obj, cells=None):
        return self.DataRow(self, data_obj, cells=cells, data=self._row_meta)

    def _build_total_cell(self, row, column, data_obj):
        return self._build_cell(row, column, data_obj, column.total_value)

    def _build_cell(self, row, column, data_obj, value_getter=None):
        return self.DataCell(
            self,
            row,
            column,
            data=self._cell_meta,
            value=self._get_cell_value(data_obj, column, value_getter or column.value)
        )

    def _get_cell_value(self, obj, column, value_getter):

        if callable(value_getter):
            if column.value_args:
                value = value_getter(obj, **column.value_args) # Make callback if given
            else:
                value = value_getter(obj)
            return self._coerce_value(column, value)

        if isinstance(value_getter, basestring): # Try dict or attr lookup if string first
            try:
                value = self._get_cell_value_from_string(obj, value_getter)
                return self._coerce_value(column, value)
            except:
                logger.debug('Could not get value %s from object %s. Assuming static value.',
                            value_getter, repr(obj), exc_info=True)
                return value_getter

        return value_getter # Assume value passed in is static value

    def _get_cell_value_from_string(self, obj, value_getter):
        val = obj
        # Allow . access to other values
        for attr in value_getter.split('.'):
            # Check dict/list val first
            try:
                val = val[attr]
            except (KeyError, IndexError, TypeError):
                # Not dict/list val, use getattr
                val = getattr(val, attr)

            # Allow traversing callables
            if callable(val):
                val = val()

        return val

    def _coerce_value(self, column, value):
        type = column.type
        if not value:
            # Use Default value if the value is None
            return column.get_default_value(value)

        if column.coerce_value:
            # If column defines its own value coercion, use that
            return column.coerce_value(value)

        if type == "datetime":
            if not column.output_format:
                column.output_format = "m/d/Y h:i A"
            if isinstance(value, basestring):
                formatter = column.input_format or '%Y-%m-%d %H:%M:%S.%f'
                return datetime.datetime.strptime(value, formatter)
            if isinstance(value, int) or isinstance(value, long) or isinstance(value, Decimal):
                return datetime.datetime.fromtimestamp(Decimal(str(value)))
        elif type == "date":
            if not column.output_format:
                column.output_format = "m/d/Y"

            if isinstance(value, basestring):
                formatter = column.input_format or '%Y-%m-%d'
                return datetime.datetime.strptime(value, formatter)
            if isinstance(value, int) or isinstance(value, long) or isinstance(value, Decimal):
                return datetime.datetime.fromtimestamp(Decimal(str(value)))
        elif type == "int":
            return int(value)
        elif type == "long":
            return long(value)
        elif type == "decimal":
            # Add the precision to round decimal to if not found
            if not column.precision or not isinstance(column.precision, int):
                column.precision = 2
            return Decimal(str(value))
        elif type == "bool":
            return bool(value)
        elif type == "null":
            return None
        elif type == "string":
            return unicode(value)

        return value

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        for row in self.rows:
            for column in self.columns:
                for cell in row.cells:
                    yield row, column, cell


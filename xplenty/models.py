from dateutil.parser import parse as parse_datetime


# from kennethreitz/python-github3
def to_python(obj,
    in_dict,
    str_keys=None,
    date_keys=None,
    int_keys=None,
    float_keys=None,
    object_map=None,
    bool_keys=None,
    dict_keys=None,
    list_keys=None,
    **kwargs):
    """Extends a given object for API Consumption.

    :param obj: Object to extend.
    :param in_dict: Dict to extract data from.
    :param string_keys: List of in_dict keys that will be extracted as strings.
    :param date_keys: List of in_dict keys that will be extrad as datetimes.
    :param object_map: Dict of {key, obj} map, for nested object results.
    """

    d = {}

    if str_keys:
        for in_key in str_keys:
            d[in_key] = str(in_dict.get(in_key))

    if date_keys:
        for in_key in date_keys:
            in_date = in_dict.get(in_key)
            try:
                out_date = parse_datetime(in_date)
            except (ValueError, TypeError, AttributeError):
                out_date = None

            d[in_key] = out_date

    if int_keys:
        for in_key in int_keys:
            if (in_dict is not None) and (in_dict.get(in_key) is not None):
                try:
                    out_int = int(in_dict.get(in_key))
                except (ValueError, TypeError):
                    out_int = None
                d[in_key] = out_int

    if float_keys:
        for in_key in float_keys:
            if (in_dict is not None) and (in_dict.get(in_key) is not None):
                try:
                    out_float = float(in_dict.get(in_key))
                except (ValueError, TypeError):
                    out_float = None
                d[in_key] = out_float

    if bool_keys:
        for in_key in bool_keys:
            if in_dict.get(in_key) is not None:
                d[in_key] = bool(in_dict.get(in_key))

    if dict_keys:
        for in_key in dict_keys:
            if in_dict.get(in_key) is not None:
                d[in_key] = dict(in_dict.get(in_key))

    if object_map:
        for (k, v) in list(object_map.items()):
            if in_dict.get(k):
                if isinstance(v, list):
                    v = v[0]
                    d[k] = [v.new_from_dict(o) for o in in_dict.get(k)]
                else:
                    d[k] = v.new_from_dict(in_dict.get(k))

    if list_keys:
        for in_key in list_keys:
            if in_dict.get(in_key) is not None:
                d[in_key] = list(in_dict.get(in_key))

    obj.__dict__.update(d)
    obj.__dict__.update(kwargs)

    return obj


class BaseModel(object):

    _strs = []
    _ints = []
    _dates = []
    _bools = []
    _dicts = []
    _floats = []
    _map = {}
    _lists = []
    _pks = []

    def __init__(self):
        self._bootstrap()
        self._h = None
        super(BaseModel, self).__init__()

    def __repr__(self):
        return "<resource '{0}'>".format(self._id)

    def _bootstrap(self):
        """Bootstraps the model object based on configured values."""

        for attr in self._keys():
            setattr(self, attr, None)

    def _keys(self):
        return (
            self._strs + self._ints + self._dates + self._lists +
            self._bools + list(self._map.keys()) + self._dicts + self._floats
        )

    @property
    def _id(self):
        try:
            return getattr(self, self._pks[0])
        except IndexError:
            return None

    @property
    def _ids(self):
        """The list of primary keys to validate against."""
        for pk in self._pks:
            yield getattr(self, pk)

        for pk in self._pks:

            try:
                yield str(getattr(self, pk))
            except ValueError:
                pass

    def dict(self):
        return {
            k: getattr(self, k)
            for k in self._keys()
        }

    @classmethod
    def new_from_dict(cls, d, h=None, **kwargs):

        d = to_python(
            obj=cls(),
            in_dict=d,
            str_keys=cls._strs,
            int_keys=cls._ints,
            float_keys=cls._floats,
            date_keys=cls._dates,
            bool_keys=cls._bools,
            dict_keys=cls._dicts,
            object_map=cls._map,
            list_keys=cls._lists,
            _h=h
        )

        d.__dict__.update(kwargs)

        return d


class Cluster(BaseModel):
    """Xplenty Cluster."""

    _strs = [
        'name', 'description', 'status', 'type', 'url', 'html_url', 'stack',
        'region', 'zone', 'master_instance_type', 'slave_instance_type'
    ]
    _ints = ['id', 'owner_id', 'nodes', 'running_jobs_count', 'time_to_idle', 'plan_id']
    _floats = ['master_spot_price', 'slave_spot_price', 'master_spot_percentage', 'slave_spot_percentage']
    _dates = ['created_at', 'updated_at', 'available_since', 'terminated_at', 'idle_since']
    _bools = ['terminate_on_idle', 'terminated_on_idle', 'allow_fallback']
    _lists = ['bootstrap_actions']
    _dicts = ['creator']
    _pks = ['id']

    def __repr__(self):
        return "<Cluster '{0}'>".format(self.name)

class Component(BaseModel):
    """Xplenty output component."""

    _strs = ['name', 'type']
    _lists = ['fields']
    _pks = ['name']

    def __repr__(self):
        return "<Component '{0}'>".format(self.name)


class Output(BaseModel):
    """Xplenty job output."""

    _ints = ['id', 'records_count', 'bytes_count']
    _strs = ['name', 'preview_url', 'url', 'preview_type', 'path']
    _dates = ['created_at', 'updated_at']
    _bools = ['can_preview', 'can_download']
    _map = {
        'component': Component
    }
    _pks = ['id']

    def __repr__(self):
        return "<Output '{0}'>".format(self.name)


class Creator(BaseModel):
    """Xplenty job creator."""

    _ints = ['id']
    _strs = ['type', 'url', 'html_url', 'display_name']
    _pks = ['id']

    def __repr__(self):
        return "<Creator '{0}'>".format(self.display_name)


class Job(BaseModel):
    """Xplenty Job."""

    _strs = ['errors', 'status', 'url', 'html_url', 'log_url']
    _ints = ['id', 'cluster_id', 'outputs_count', 'owner_id', 'package_id', 'runtime_in_seconds']
    _floats = ['progress']
    _dates = ['created_at', 'started_at', 'updated_at', 'failed_at', 'completed_at']
    _dicts = ['variables', 'dynamic_variables']
    _map = {
        'outputs': [Output],
        'cluster': Cluster,
        'creator': Creator
    }
    _pks = ['id']

    def __repr__(self):
        return "<Job '{0}'>".format(self.id)


class AccountLimits(BaseModel):
    """Xplenty Account limits."""

    _ints = ['limit', 'remaining']

    def __repr__(self):
        return "<AccountLimits '{0}'>".format(self.name)


class Package(BaseModel):
    """Xplenty Package."""

    _strs = ['name', 'description', 'url', 'html_url', 'status']
    _ints = ['id', 'owner_id']
    _floats = []
    _dates = ['created_at', 'updated_at']
    _dicts = ['variables']
    _pks = ['id']

    def __repr__(self):
        return "<Package '{0}'>".format(self.name)


class Schedule(BaseModel):
    """Xplenty Schedule."""

    _strs = ['name', 'description', 'url', 'html_url', 'interval_unit', 'last_run_status', 'status']
    _ints = ['id', 'owner_id', 'interval_amount', 'execution_count']
    _floats = []
    _dates = ['created_at', 'updated_at', 'start_at', 'next_run_at', 'last_run_at']
    _dicts = ['variables', 'task']
    _pks = ['id']

    def __repr__(self):
        return "<Schedule '{0}'>".format(self.name)

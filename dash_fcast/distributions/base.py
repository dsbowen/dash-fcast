class Base():
    def __init__(self, id, *args, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs)

    @classmethod
    def get_id(cls, id, type='state'):
        """
        Parameters
        ----------
        id : str

        type : str, default='state'
            Type of object associated with the moments distribution.

        Returns
        -------
        id dictionary : dict
            Dictionary identifier.
        """
        return {'dist-cls': cls.__name__, 'dist-id': id, 'type': type}
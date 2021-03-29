from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Couriers


class CourierSerializer(serializers.ModelSerializer):
    id_field_name = "courier_id"

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data', None)
        super().__init__(*args, **kwargs)

        self.validate_data(data)

    def check_extra(self, extra, err, id_):
        if len(extra) !=0:
            err["id"] = id_
            err["extra fields"] = [field for field in extra]

    def check_missing(self, missing, err, id_):
        if len(missing) != 0:
            err["id"] = id_
            err["missing fields"] = [field for field in missing]

    def check_fields(self, missing, extra, id_):
        err = {}
        self.check_extra(extra, err, id_)
        self.check_missing(missing, err, id_)
        return err

    def validate_data(self, data):
        errors = []
        fields = set(self.fields)
        if data and isinstance(data, list):
            for courier in data:
                in_ = set(courier.keys())
                missing = fields - in_
                extra = in_ - fields
                id_ = courier.get(self.id_field_name)
                err = self.check_fields(missing, extra, id_)
                errors.append(err) if len(err) else None
        elif data and isinstance(data, dict):
            if "data" in data.keys():
                return
            in_ = set(data.keys())
            extra = in_ - fields
            id_ = self.instance.pk
            err = {}
            self.check_extra(extra, err, id_)
            errors.append(err) if len(err) else None
        if len(errors):
            raise ValidationError(detail=errors)

    class Meta:
        model = Couriers
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours', )


class SingleCourierSerializer(CourierSerializer):
    rating = serializers.FloatField()

    class Meta:
        model = Couriers
        fields = '__all__'
        depth = 1

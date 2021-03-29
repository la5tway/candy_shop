from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Couriers


class CourierSerializer(serializers.ModelSerializer):
    id_field_name = "courier_id"

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data', None)
        super().__init__(*args, **kwargs)

        self.validate_data(data)

    def check_extra(self, extra, err, pk):
        if len(extra):
            err["id"] = pk
            err["extra fields"] = [field for field in extra]

    def check_missing(self, missing, err, pk):
        if len(missing):
            err["id"] = pk
            err["missing fields"] = [field for field in missing]

    def check_fields(self, missing, extra, pk):
        err = {}
        self.check_extra(extra, err, pk)
        self.check_missing(missing, err, pk)
        return err

    def validate_data(self, data):
        if data:
            errors = []
            fields = set(self.fields)
            if isinstance(data, list):
                for courier in data:
                    fields_in = set(courier.keys())
                    missing = fields - fields_in
                    extra = fields_in - fields
                    pk = courier.get(self.id_field_name)
                    err = self.check_fields(missing, extra, pk)
                    errors.append(err) if len(err) else None
            elif isinstance(data, dict):
                if "data" in data.keys():
                    return
                fields_in = set(data.keys())
                extra = fields_in - fields
                pk = self.instance.pk
                err = {}
                self.check_extra(extra, err, pk)
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

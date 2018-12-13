def filterFields(allFields, dropFields):
    fields = allFields.replace("\n", "").split(",")
    fields = [field.split(" ")[0] for field in fields]
    fields = [field for field in fields if field not in dropFields and field != '']
    return fields
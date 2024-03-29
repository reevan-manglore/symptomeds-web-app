import types
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import mysql.connector
from mysql.connector import cursor
import json
from posts import post


app = Flask(__name__)

app.register_blueprint(post, url_prefix="/post/")

CORS(app)

api = Api(app)


class Disease(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        symptoms = request.args.get("symptoms")
        symptoms = symptoms.split(",")
        symptoms = ",".join(map(str, symptoms))
        print("disease are {}".format(symptoms))
        cursor = db.cursor()
        query = """
            select dName,count(*) as frequency from
            disease d,diseaseSymptoms ds,symptoms s
            where d.dId = ds.dId
            and ds.sId = s.sId
            and sName in (%s)
            group by dName
            order by frequency desc;
        """
        cursor.execute(query % (symptoms))
        record = cursor.fetchall()
        cursor.close()
        print(record)
        return record


class Symptoms(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        disease = request.args.get("disease")
        print("disease names are = %s" % (disease))
        query = """
            select sName
            from symptoms
            where sId in (
	            select ds.sId
                from diseaseSymptoms ds,disease d
	            where ds.dId = d.dId
	            and dName = "%s"
            );
        """
        cursor = db.cursor()
        cursor.execute(query % (disease))
        symptoms = cursor.fetchall()
        cursor.close()
        result = []
        for i in symptoms:
            result.append(i[0])
        return result


class SymptomsAndParts(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        disease = request.args.get("disease")
        print("disease names are = %s" % (disease))
        query = """
             select sName,sPart from
             disease d,diseaseSymptoms ds,symptoms s
             where d.dId = ds.dId
             and ds.sId = s.sId
             and dName = "%s";
        """
        cursor = db.cursor()
        cursor.execute(query % (disease))
        result = cursor.fetchall()
        cursor.close()
        return result


class Medicine(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        query = """
              select mName,modeOfAdministration
              from medicine
              where mId in (
	                select mId
                    from treatment t,disease d
                    where d.dId = t.dId
                    and dName = "%s"
                );

        """
        disease = request.args.get("disease")
        cursor = db.cursor()
        cursor.execute(query % (disease))
        result = cursor.fetchall()
        cursor.close()
        return result


class SimilarMedicines(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        query = """
            select mName,modeOfAdministration
            from medicine
            where mId in (
	        select similar
	        from  similarMedicine
	        where mId in ( select s.mId
				 from medicine m,similarMedicine s
                 where m.mId = s.similar
                 and m.mName = "%s"
				)
            );
        """
        name = request.args.get("medicine")
        cursor = db.cursor()
        cursor.execute(query % (name))
        result = cursor.fetchall()
        cursor.close()
        return result


class Chemicals(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        query = """
            select cName
            from chemicals
            where cId in(
	            select cId
	            from medicineContents
	            where mId = (select mId from medicine where mName = "%s")
            );
        """
        medicine = request.args.get("medicine")
        cursor = db.cursor()
        cursor.execute(query % (medicine))
        result = cursor.fetchall()
        return result


class MedicineWithChemicals(Resource):
    def get(self):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )

        query = """
            select mName
            from medicine m,chemicals c,medicineContents cc
            where m.mId = cc.mId and c.cId = cc.cId
            and c.cName = "%s";
         """
        cursor = db.cursor()
        chemical = request.args.get("chemical")
        cursor.execute(query % (chemical))
        result = cursor.fetchall()
        cursor.close()
        return result


class AutoCompletion(Resource):
    def get(self, table):
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database='project'
        )
        data = []
        #query = 'select {0} from {1} where {0} like "{2}%"'
        # this will fetch all data from given table
        query = 'select distinct {0} from {1}'
        val = request.args.get("query")
        if(table == "disease"):
            query = query.format("dName", table)
        elif(table == "symptoms"):
            query = query.format("sName", table)
        elif(table == "medicine"):
            query = query.format("mName", table)
        elif(table == "chemicals"):
            query = query.format("cName", table)
        else:
            return {"message": "an error in query parameter"}, 400
        cursor = db.cursor()
        try:
            cursor.execute(query)
        except:
            print("error ocuured while executing sql")
            cursor.close()
            return {"message": "error occured"}, 500
        result = cursor.fetchall()
        for i in result:
            data.append(i[0])
        db.close()
        return data


api.add_resource(Disease, "/disease/")
api.add_resource(Symptoms, "/symptoms/")
api.add_resource(SymptomsAndParts, "/symptoms-and-parts/")
api.add_resource(Medicine, "/medicines/")
api.add_resource(SimilarMedicines, "/similar-medicines/")
api.add_resource(Chemicals, "/show-chemicals/")
api.add_resource(MedicineWithChemicals, "/medicine-with-chemical/")
api.add_resource(AutoCompletion, "/search/<string:table>")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")

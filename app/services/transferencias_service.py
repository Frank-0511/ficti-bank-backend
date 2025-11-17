from app.db.session import get_session
from app.models.account import Cuenta, Movimiento
from app.schemas.transferencias_schema import TransferenciaRequest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError


class TransferenciaService:

    @staticmethod
    def realizar_transferencia(data: TransferenciaRequest):

        db = next(get_session())
        try:
            # ----------------------------------------
            # 1. Obtener cuentas
            # ----------------------------------------
            origen = db.query(Cuenta).filter(Cuenta.NroCta == data.cuenta_origen).first()
            destino = db.query(Cuenta).filter(Cuenta.NroCta == data.cuenta_destino).first()

            if not origen:
                raise Exception("La cuenta de origen no existe")

            if not destino:
                raise Exception("La cuenta de destino no existe")

            # ----------------------------------------
            # 2. Validar embargo
            # ----------------------------------------
            if origen.Fech_Bloq is not None:
                raise Exception("La cuenta de origen está embargada o bloqueada")

            # ----------------------------------------
            # 3. Validar cuenta a plazo
            # ----------------------------------------
            if origen.TipoCta == "PF":     # Ajustar según códigos reales de tu BD
                raise Exception("La cuenta de origen es de plazo fijo y no permite transferencias")

            # ----------------------------------------
            # 4. Validar saldo
            # ----------------------------------------
            monto = Decimal(str(data.monto))

            if origen.SaldAct < monto:
                raise Exception("Saldo insuficiente")

            # ----------------------------------------
            # 5. Actualizar saldos
            # ----------------------------------------
            origen.SaldAct -= monto
            destino.SaldAct += monto

            # ----------------------------------------
            # 6. Registrar movimiento ORIGEN
            # ----------------------------------------
            mov_origen = Movimiento(
                TipoCta=origen.TipoCta,    # <<--- AGREGADO
                NroCta=origen.NroCta,
                NroOperNumber=TransferenciaService._next_oper_number(db, origen.NroCta),
                Fech_Ope=date.today(),
                CodUsu=data.cod_usuario,
                TipoMov="TR",
                MonOpe=monto * -1,
                Estado="A"
            )

            # ----------------------------------------
            # 7. Registrar movimiento DESTINO
            # ----------------------------------------
            mov_destino = Movimiento(
                TipoCta=destino.TipoCta,   # <<--- AGREGADO
                NroCta=destino.NroCta,
                NroOperNumber=TransferenciaService._next_oper_number(db, destino.NroCta),
                Fech_Ope=date.today(),
                CodUsu=data.cod_usuario,
                TipoMov="TR",
                MonOpe=monto,
                Estado="A"
            )

            db.add(mov_origen)
            db.add(mov_destino)

            db.commit()
            db.refresh(origen)
            db.refresh(destino)

            return {
                "mensaje": "Transferencia realizada correctamente",
                "saldo_origen": float(origen.SaldAct),
                "saldo_destino": float(destino.SaldAct)
            }

        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error en la BD: {str(e)}")

        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def _next_oper_number(db, nro_cta: str):
        last = (
            db.query(Movimiento)
            .filter(Movimiento.NroCta == nro_cta)
            .order_by(Movimiento.NroOperNumber.desc())
            .first()
        )
        return 1 if last is None else last.NroOperNumber + 1

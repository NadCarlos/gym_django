# CERMED Gym Admin

CERMED Gym Admin is the internal backoffice for administrative, financial and rehabilitation operations at CERMED. This file defines domain language for agents and maintainers; it is not an implementation guide.

## Language

**CERMED**:
The medical and rehabilitation business that uses this backoffice to manage patients, agendas, attendance, treatments and financial operations.
_Avoid_: Gym, generic clinic, tenant

**Paciente**:
A person receiving care or services from CERMED. A patient can appear in administrative and rehabilitation flows depending on their care context.
_Avoid_: Cliente, socio, usuario

**Profesional**:
A person who provides care or services to patients, such as medical, rehabilitation or administrative service professionals.
_Avoid_: Doctor when the role is broader, instructor

**Turno**:
A scheduled appointment between a patient and a professional or service area at a specific date and time.
_Avoid_: Reserva, slot

**Agenda**:
The schedule availability and appointment structure for a professional, service or area.
_Avoid_: Calendario when referring to the domain object

**Disponibilidad Horaria**:
The recurring time windows in which a rehabilitation professional can receive assigned agenda entries.
_Avoid_: Turno, Agenda when referring only to the professional's available capacity

**Asistencia**:
The record that a patient attended or checked in for a scheduled or expected activity.
_Avoid_: Presencia, check-in in domain text

**Tratamiento**:
A care plan or therapeutic process assigned to a patient, often involving one or more professionals.
_Avoid_: Plan when referring to clinical/rehabilitation care

**Prestación**:
A specific service provided to a patient and potentially billable or associated with a plan.
_Avoid_: Servicio when the system term is prestación

**Obra Social**:
The health insurance or coverage entity associated with a patient or payment/billing flow.
_Avoid_: Seguro, cobertura when naming the domain object

**Plan**:
An administrative or commercial plan associated with patient services, quotas or billing.
_Avoid_: Tratamiento when referring to commercial/admin plans

**Cuota**:
A scheduled fee or installment owed under a plan or administrative arrangement.
_Avoid_: Pago; a payment settles a quota but is not the quota itself

**Pago**:
The act or record of money received or issued to settle a financial obligation.
_Avoid_: Cuota when referring to the money movement

**Orden de Pago**:
A financial document or workflow used to manage an outgoing payment obligation.
_Avoid_: Pago when referring to the order/document before settlement

**Libro de Ventas**:
The sales ledger used for financial reporting and tracking sale records.
_Avoid_: Reporte de ventas when referring to the ledger itself

**Beneficiario**:
A person or entity that receives or is associated with a financial benefit/payment in finance workflows.
_Avoid_: Paciente unless the person is specifically receiving care

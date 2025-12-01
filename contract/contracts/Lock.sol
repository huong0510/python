// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract HospitalBillContract {
    struct Bill {
        uint256 patientId;
        string patientName;
        string assignedDoctorName;
        string addressDetail;
        string mobile;
        string symptoms;
        uint256 admitDate;
        uint256 releaseDate;
        uint256 daySpent;
        uint256 medicineCost;
        uint256 roomCharge;
        uint256 doctorFee;
        uint256 otherCharge;
        uint256 total;
    }

    Bill[] public bills;

    event BillCreated(uint256 indexed patientId, string patientName, uint256 total);
    event DebugLog(string message, uint256 value);

    function createBill(
        uint256 patientId,
        string memory patientName,
        string memory assignedDoctorName,
        string memory addressDetail,
        string memory mobile,
        string memory symptoms,
        uint256 admitDate,
        uint256 releaseDate,
        uint256 daySpent,
        uint256 medicineCost,
        uint256 roomCharge,
        uint256 doctorFee,
        uint256 otherCharge
    ) public {
        require(patientId > 0, "Invalid patient ID");
        require(daySpent >= 0, "Invalid daySpent");
        require(releaseDate >= admitDate, "Release date before admit date");
        emit DebugLog("Patient ID", patientId);
        emit DebugLog("Day Spent", daySpent);
        emit DebugLog("Medicine Cost", medicineCost);
        emit DebugLog("Room Charge", roomCharge);
        emit DebugLog("Doctor Fee", doctorFee);
        emit DebugLog("Other Charge", otherCharge);
        uint256 total = medicineCost + roomCharge + doctorFee + otherCharge;

        emit DebugLog("Total cost calculated", total);

        Bill memory bill = Bill({
            patientId: patientId,
            patientName: patientName,
            assignedDoctorName: assignedDoctorName,
            addressDetail: addressDetail,
            mobile: mobile,
            symptoms: symptoms,
            admitDate: admitDate,
            releaseDate: releaseDate,
            daySpent: daySpent,
            medicineCost: medicineCost,
            roomCharge: roomCharge,
            doctorFee: doctorFee,
            otherCharge: otherCharge,
            total: total
        });

        bills.push(bill);
        emit BillCreated(patientId, patientName, total);
    }

    function getBill(uint256 index) public view returns (Bill memory) {
        require(index < bills.length, "Invalid bill index");
        return bills[index];
    }

    function getBillCount() public view returns (uint256) {
        return bills.length;
    }
}

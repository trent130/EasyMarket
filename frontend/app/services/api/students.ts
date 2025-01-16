import { PaginatedResponse, Student } from "@/types/common";
import { fetchWrapper } from "@/utils/fetchWrapper";

interface StudentQueryParams {
    page?: number;
    pageSize?: number;
    search?: string;
    course?: string;
    year?: number;
    status?: Student['status'];
}

// Merged content from students.ts and studentsApi.ts
export const studentFunctions = {
        getStudents: (params?: Record<string, string | number>) =>
            fetchWrapper<PaginatedResponse<Student>>('/api/students', { params }),
        
        getStudentDetails: (id: number) =>
            fetchWrapper<Student>(`/api/students/${id}`),
        updateStudent: (id: number, data: Partial<Student>) =>
            fetchWrapper(`/api/students/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            }),
        
        deleteStudent: (id: number) =>
            fetchWrapper(`/api/students/${id}`, {
                method: 'DELETE'
            })
};

// Add any additional functions or logic as needed

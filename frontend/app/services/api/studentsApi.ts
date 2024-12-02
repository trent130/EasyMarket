import { fetchWrapper } from '../../utils/fetchWrapper';
import { PaginatedResponse } from '../../types/common';

interface Student {
    id: number;
    studentId: string;
    firstName: string;
    lastName: string;
    email: string;
    course: string;
    year: number;
    status: 'active' | 'inactive' | 'graduated';
}

interface StudentQueryParams {
    page?: number;
    pageSize?: number;
    search?: string;
    course?: string;
    year?: number;
    status?: Student['status'];
}

export const studentsApi = {
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

export type StudentsApi = typeof studentsApi; 
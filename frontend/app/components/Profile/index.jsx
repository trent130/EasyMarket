import React, { useState, useEffect } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Box, Avatar, Button, TextField, Typography, Alert } from '@mui/material';
import { Edit as EditIcon } from '@mui/icons-material';
import api from '../../services/api';
import './styles.css';

const Profile = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const formik = useFormik({
        initialValues: {
            username: '',
            first_name: '',
            last_name: '',
            email: '',
            avatar: null
        },
        validationSchema: Yup.object({
            username: Yup.string().required('Username is required'),
            email: Yup.string().email('Invalid email').required('Email is required'),
            first_name: Yup.string().required('First name is required'),
            last_name: Yup.string().required('Last name is required')
        }),
        onSubmit: async (values) => {
            try {
                setLoading(true);
                setError(null);
                const formData = new FormData();
                
                Object.keys(values).forEach(key => {
                    if (values[key] !== null) {
                        formData.append(key, values[key]);
                    }
                });

                await api.patch('/api/profiles/me/', formData);
                setSuccess(true);
            } catch (err) {
                setError(err.response?.data?.message || 'An error occurred');
            } finally {
                setLoading(false);
            }
        }
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                setLoading(true);
                const response = await api.get('/api/profiles/me/');
                const profileData = response.data;
                
                formik.setValues({
                    username: profileData.username || '',
                    first_name: profileData.first_name || '',
                    last_name: profileData.last_name || '',
                    email: profileData.email || '',
                    avatar: null
                });
            } catch (err) {
                setError('Failed to load profile');
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleAvatarChange = (event) => {
        const file = event.currentTarget.files[0];
        formik.setFieldValue('avatar', file);
    };

    return (
        <Box className="profile-container">
            <Typography variant="h4" gutterBottom>
                Profile
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                    Profile updated successfully!
                </Alert>
            )}

<form onSubmit={formik.handleSubmit} aria-label="Profile Update Form">
                <Box className="avatar-section">
                    <Avatar
                        src={formik.values.avatar ? URL.createObjectURL(formik.values.avatar) : undefined}
                        sx={{ width: 100, height: 100 }}
                    />
                    <Button
                        component="label"
                        startIcon={<EditIcon />}
                        sx={{ mt: 1 }}
                    >
                        Change Avatar
                        <input
                            type="file"
                            hidden
                            accept="image/*"
                            onChange={handleAvatarChange}
                        />
                    </Button>
                </Box>

                <TextField
                    fullWidth
                    id="username"
                    name="username"
                    label="Username"
                    value={formik.values.username}
                    onChange={formik.handleChange}
                    error={formik.touched.username && Boolean(formik.errors.username)}
                    helperText={formik.touched.username && formik.errors.username}
                    margin="normal"
                />

                <TextField
                    fullWidth
                    id="first_name"
                    name="first_name"
                    label="First Name"
                    value={formik.values.first_name}
                    onChange={formik.handleChange}
                    error={formik.touched.first_name && Boolean(formik.errors.first_name)}
                    helperText={formik.touched.first_name && formik.errors.first_name}
                    margin="normal"
                />

                <TextField
                    fullWidth
                    id="last_name"
                    name="last_name"
                    label="Last Name"
                    value={formik.values.last_name}
                    onChange={formik.handleChange}
                    error={formik.touched.last_name && Boolean(formik.errors.last_name)}
                    helperText={formik.touched.last_name && formik.errors.last_name}
                    margin="normal"
                />

                <TextField
                    fullWidth
                    id="email"
                    name="email"
                    label="Email"
                    value={formik.values.email}
                    onChange={formik.handleChange}
                    error={formik.touched.email && Boolean(formik.errors.email)}
                    helperText={formik.touched.email && formik.errors.email}
                    margin="normal"
                />

                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                    sx={{ mt: 2 }}
                >
                    {loading ? 'Updating...' : 'Update Profile'}
                </Button>
            </form>
        </Box>
    );
};

export default Profile; 

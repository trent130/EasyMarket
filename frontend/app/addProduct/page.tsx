"use client";

import React from "react";
import ProductForm from "@/components/Product/ProductForm";
import DashboardLayout from "@/components/DashboardLayout";

const AddProductPage = () => {
    return (
        <DashboardLayout>
            <div>
                <ProductForm />
            </div>
        </DashboardLayout>
    );
};  

export default AddProductPage;